import io
from pathlib import Path

import pytest
from rich.console import Console

from commands.refs_command import RefsCommand
from core.models import CommandStatus, RuntimeContext


def make_context(base_dir: Path) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="1",
        display_mode="standard",
        project_root=base_dir,
    )


def test_refs_command_usage(tmp_path):
    context = make_context(tmp_path)
    result = RefsCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Usage: /refs <symbol>" in output


def test_refs_found(tmp_path):
    # Setup files: definition in service.py, references in app.py
    (tmp_path / "service.py").write_text(
        "class ConfigService:\n"
        "    pass\n",
        encoding="utf-8"
    )
    (tmp_path / "app.py").write_text(
        "from service import ConfigService\n"
        "config = ConfigService()\n",
        encoding="utf-8"
    )

    context = make_context(tmp_path)
    result = RefsCommand.execute(("ConfigService",), context)
    assert result == CommandStatus.HANDLED
    
    output = context.console.file.getvalue()
    assert "References (2)" in output
    assert "app.py:1" in output
    assert "app.py:2" in output
    # Definition line in service.py:1 should be excluded
    assert "service.py:1" not in output


def test_refs_missing(tmp_path):
    context = make_context(tmp_path)
    result = RefsCommand.execute(("GhostSymbol",), context)
    assert result == CommandStatus.HANDLED
    
    output = context.console.file.getvalue()
    assert "No references found for 'GhostSymbol'" in output
