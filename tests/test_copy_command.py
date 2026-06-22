import io
from pathlib import Path

import pytest
from rich.console import Console

from commands.copy_command import CopyCommand
from core.models import CommandStatus, RuntimeContext
from routing.command_router import CommandRouter


def make_context(base_dir: Path) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="1",
        display_mode="standard",
        project_root=base_dir,
    )


def test_copy_command_usage(tmp_path):
    context = make_context(tmp_path)
    result = CopyCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Usage: /copy <source> <destination>" in output


def test_copy_file_success(tmp_path):
    src = tmp_path / "old.txt"
    src.write_text("hello")
    context = make_context(tmp_path)

    result = CopyCommand.execute(("old.txt", "new.txt"), context)
    assert result == CommandStatus.HANDLED
    assert src.exists()
    assert (tmp_path / "new.txt").read_text() == "hello"
    output = context.console.file.getvalue()
    assert "Copied: old.txt -> new.txt" in output


def test_copy_file_creates_parent_dir(tmp_path):
    src = tmp_path / "old.txt"
    src.write_text("hello")
    context = make_context(tmp_path)

    result = CopyCommand.execute(("old.txt", "nested/deep/new.txt"), context)
    assert result == CommandStatus.HANDLED
    assert src.exists()
    assert (tmp_path / "nested" / "deep" / "new.txt").read_text() == "hello"


def test_copy_dir_recursive_success(tmp_path):
    src_dir = tmp_path / "old_dir"
    src_dir.mkdir()
    (src_dir / "file.txt").write_text("content")
    context = make_context(tmp_path)

    result = CopyCommand.execute(("old_dir", "new_dir"), context)
    assert result == CommandStatus.HANDLED
    assert src_dir.exists()
    assert (tmp_path / "new_dir" / "file.txt").read_text() == "content"


def test_copy_root_escape_fails(tmp_path):
    src = tmp_path / "old.txt"
    src.write_text("hello")
    context = make_context(tmp_path)

    result = CopyCommand.execute(("old.txt", "../../escaped.txt"), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Error: Access denied: path" in output
    assert not (tmp_path.parent / "escaped.txt").exists()


def test_copy_ignored_dir_fails(tmp_path):
    src = tmp_path / "old.txt"
    src.write_text("hello")
    (tmp_path / ".git").mkdir()
    context = make_context(tmp_path)

    result = CopyCommand.execute(("old.txt", ".git/config"), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Error: Access denied: path" in output
    assert not (tmp_path / ".git" / "config").exists()


def test_copy_command_routing(tmp_path):
    src = tmp_path / "old.txt"
    src.write_text("hello")
    context = make_context(tmp_path)

    result = CommandRouter.route("/copy old.txt new.txt", context)
    assert result == CommandStatus.HANDLED
    assert src.exists()
    assert (tmp_path / "new.txt").exists()
