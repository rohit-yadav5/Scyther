import io
from pathlib import Path

import pytest
from rich.console import Console

from commands.move_command import MoveCommand
from core.models import CommandStatus, RuntimeContext
from routing.command_router import CommandRouter


def make_context(base_dir: Path) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="1",
        display_mode="standard",
        project_root=base_dir,
    )


def test_move_command_usage(tmp_path):
    context = make_context(tmp_path)
    result = MoveCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Usage: /move <source> <destination>" in output


def test_move_file_success(tmp_path):
    src = tmp_path / "old.txt"
    src.write_text("hello")
    context = make_context(tmp_path)

    result = MoveCommand.execute(("old.txt", "new.txt"), context)
    assert result == CommandStatus.HANDLED
    assert not src.exists()
    assert (tmp_path / "new.txt").read_text() == "hello"
    output = context.console.file.getvalue()
    assert "Moved: old.txt -> new.txt" in output


def test_move_file_creates_parent_dir(tmp_path):
    src = tmp_path / "old.txt"
    src.write_text("hello")
    context = make_context(tmp_path)

    result = MoveCommand.execute(("old.txt", "nested/deep/new.txt"), context)
    assert result == CommandStatus.HANDLED
    assert not src.exists()
    assert (tmp_path / "nested" / "deep" / "new.txt").read_text() == "hello"


def test_move_dir_success(tmp_path):
    src_dir = tmp_path / "old_dir"
    src_dir.mkdir()
    (src_dir / "file.txt").write_text("content")
    context = make_context(tmp_path)

    result = MoveCommand.execute(("old_dir", "new_dir"), context)
    assert result == CommandStatus.HANDLED
    assert not src_dir.exists()
    assert (tmp_path / "new_dir" / "file.txt").read_text() == "content"


def test_move_root_escape_fails(tmp_path):
    src = tmp_path / "old.txt"
    src.write_text("hello")
    context = make_context(tmp_path)

    result = MoveCommand.execute(("old.txt", "../../escaped.txt"), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Error: Access denied: path" in output
    assert src.exists()


def test_move_ignored_dir_fails(tmp_path):
    src = tmp_path / "old.txt"
    src.write_text("hello")
    (tmp_path / ".git").mkdir()
    context = make_context(tmp_path)

    result = MoveCommand.execute(("old.txt", ".git/config"), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Error: Access denied: path" in output
    assert src.exists()


def test_move_command_routing(tmp_path):
    src = tmp_path / "old.txt"
    src.write_text("hello")
    context = make_context(tmp_path)

    result = CommandRouter.route("/move old.txt new.txt", context)
    assert result == CommandStatus.HANDLED
    assert not src.exists()
    assert (tmp_path / "new.txt").exists()
