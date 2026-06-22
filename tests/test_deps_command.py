import io
from pathlib import Path

import pytest
from rich.console import Console

from scyther.commands.deps_command import DepsCommand
from scyther.core.models import CommandStatus, RuntimeContext


def make_context(base_dir: Path) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="1",
        display_mode="standard",
        project_root=base_dir,
    )


def test_deps_command_usage(tmp_path):
    context = make_context(tmp_path)
    result = DepsCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Usage: /deps <path>" in output


def test_deps_found(tmp_path):
    # Setup files: app.py imports helper and config
    (tmp_path / "helper.py").write_text("def run(): pass", encoding="utf-8")
    (tmp_path / "config.py").write_text("DEBUG = True", encoding="utf-8")
    (tmp_path / "app.py").write_text(
        "import helper\n"
        "import config\n",
        encoding="utf-8"
    )

    context = make_context(tmp_path)
    result = DepsCommand.execute(("app.py",), context)
    assert result == CommandStatus.HANDLED
    
    output = context.console.file.getvalue()
    assert "Dependencies" in output
    assert "app.py" in output
    # Check tree layout format
    assert "├─ config.py" in output or "├─ helper.py" in output
    assert "└─ " in output


def test_deps_missing_file(tmp_path):
    context = make_context(tmp_path)
    result = DepsCommand.execute(("ghost.py",), context)
    assert result == CommandStatus.HANDLED
    
    output = context.console.file.getvalue()
    assert "Error: File not found: ghost.py" in output


def test_deps_no_dependencies(tmp_path):
    (tmp_path / "empty.py").write_text("# empty file", encoding="utf-8")
    
    context = make_context(tmp_path)
    result = DepsCommand.execute(("empty.py",), context)
    assert result == CommandStatus.HANDLED
    
    output = context.console.file.getvalue()
    assert "empty.py" in output
    assert "(No dependencies found)" in output
