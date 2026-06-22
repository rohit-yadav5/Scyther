import io
from pathlib import Path

import pytest
from rich.console import Console

from commands.delete_command import DeleteCommand
from core.models import CommandStatus, RuntimeContext
from routing.command_router import CommandRouter


def make_context(base_dir: Path) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="1",  # Read + Write
        display_mode="standard",
        project_root=base_dir,
    )


def test_delete_command_usage(tmp_path):
    context = make_context(tmp_path)
    result = DeleteCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Usage: /delete [--force] <path>" in output


def test_delete_file_success(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello", encoding="utf-8")
    context = make_context(tmp_path)

    result = DeleteCommand.execute(("test.txt",), context)
    assert result == CommandStatus.HANDLED
    assert not file_path.exists()
    output = context.console.file.getvalue()
    assert "Deleted: test.txt" in output


def test_delete_dir_without_force_fails(tmp_path):
    dir_path = tmp_path / "sub"
    dir_path.mkdir()
    (dir_path / "file.txt").write_text("content")
    context = make_context(tmp_path)

    result = DeleteCommand.execute(("sub",), context)
    assert result == CommandStatus.HANDLED
    assert dir_path.is_dir()
    assert (dir_path / "file.txt").exists()

    output = context.console.file.getvalue()
    assert "Directory deletion requires:" in output
    assert "/delete --force sub" in output


def test_delete_dir_with_force_success(tmp_path):
    dir_path = tmp_path / "sub"
    dir_path.mkdir()
    (dir_path / "file.txt").write_text("content")
    context = make_context(tmp_path)

    result = DeleteCommand.execute(("--force", "sub"), context)
    assert result == CommandStatus.HANDLED
    assert not dir_path.exists()
    output = context.console.file.getvalue()
    assert "Deleted: sub" in output


def test_delete_root_escape_fails(tmp_path):
    context = make_context(tmp_path)
    result = DeleteCommand.execute(("../../escaped.txt",), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Error: Access denied: path" in output


def test_delete_ignored_dir_fails(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("config")
    context = make_context(tmp_path)

    result = DeleteCommand.execute((".git/config",), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Error: Access denied: path" in output
    assert (tmp_path / ".git" / "config").exists()


def test_delete_command_routing(tmp_path):
    file_path = tmp_path / "routed.txt"
    file_path.write_text("routed")
    context = make_context(tmp_path)

    result = CommandRouter.route("/delete routed.txt", context)
    assert result == CommandStatus.HANDLED
    assert not file_path.exists()
