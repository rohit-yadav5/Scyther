import io
from pathlib import Path

import pytest
from rich.console import Console

from scyther.commands.todo_command import TodoCommand
from scyther.core.models import CommandStatus, RuntimeContext


def make_context(base_dir: Path) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="1",
        display_mode="standard",
        project_root=base_dir,
    )


def test_todo_command_finds_keywords(tmp_path):
    (tmp_path / "file1.py").write_text("# TODO: implement X\n# simple line\n# FIXME: fix Y\n")
    (tmp_path / "file2.md").write_text("## Note\nThis is a HACK\n")
    (tmp_path / "file3.json").write_text('{"bug_report": "found a BUG here"}')

    context = make_context(tmp_path)
    result = TodoCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()

    assert "Found 4 matches" in output
    assert "file1.py:1" in output
    assert "TODO: implement X" in output
    assert "file1.py:3" in output
    assert "FIXME: fix Y" in output
    assert "file2.md:2" in output
    assert "This is a HACK" in output
    assert "file3.json:1" in output
    assert '{"bug_report": "found a BUG here"}' in output


def test_todo_command_ignores_venv(tmp_path):
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "todo.txt").write_text("# TODO inside venv")

    context = make_context(tmp_path)
    result = TodoCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    
    assert "todo.txt" not in output
