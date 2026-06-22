import io
from pathlib import Path

import pytest
from rich.console import Console

from scyther.commands.stats_command import StatsCommand
from scyther.core.models import CommandStatus, RuntimeContext
from scyther.routing.command_router import CommandRouter


def make_context(base_dir: Path) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="1",
        display_mode="standard",
        project_root=base_dir,
    )


def test_stats_command_success(tmp_path):
    # Populate project structure
    # 2 python files (one large, one small)
    (tmp_path / "foo.py").write_text("a" * 1500) # 1.5 KB -> rounds to 1 KB (1.46 KB) or wait, 1500 / 1024 = 1.46 -> rounds to 1 KB
    (tmp_path / "bar.py").write_text("a" * 500)  # 0.5 KB -> rounds to 0 KB (0.48 KB) -> wait, total size is 2000 -> 2000/1024 = 1.95 -> rounds to 2 KB
    
    # 1 markdown file
    (tmp_path / "readme.md").write_text("a" * 1200) # 1.2 KB -> rounds to 1 KB (1.17 KB)
    
    # 1 directory
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "config.json").write_text("a" * 2500) # 2.4 KB -> rounds to 2 KB (2.44 KB)

    # Total files: 4
    # Total directories: 1
    # Python files: 2
    # Markdown files: 1
    # JSON files: 1
    # Largest file: config.json (2500 bytes -> rounds to 2 KB)
    # Total project size: 1500 + 500 + 1200 + 2500 = 5700 bytes -> 5700 / 1024 = 5.56 KB -> rounds to 6 KB

    context = make_context(tmp_path)
    result = StatsCommand.execute((), context)
    assert result == CommandStatus.HANDLED

    output = context.console.file.getvalue()
    assert "Project Statistics" in output
    assert "Files: 4" in output
    assert "Directories: 1" in output
    assert "Python Files: 2" in output
    assert "Markdown Files: 1" in output
    assert "JSON Files: 1" in output
    assert "Largest File: config.json" in output
    assert "Largest File Size: 2 KB" in output
    assert "Total Project Size: 6 KB" in output


def test_stats_command_empty_dir(tmp_path):
    context = make_context(tmp_path)
    result = StatsCommand.execute((), context)
    assert result == CommandStatus.HANDLED

    output = context.console.file.getvalue()
    assert "Project Statistics" in output
    assert "Files: 0" in output
    assert "Directories: 0" in output
    assert "Largest File: None" in output
    assert "Largest File Size: 0 KB" in output
    assert "Total Project Size: 0 KB" in output


def test_stats_command_routing(tmp_path):
    context = make_context(tmp_path)
    result = CommandRouter.route("/stats", context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Project Statistics" in output
