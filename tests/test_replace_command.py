import io
from pathlib import Path

import pytest
from rich.console import Console

from commands.replace_command import ReplaceCommand
from core.models import CommandStatus, RuntimeContext
from routing.command_router import CommandRouter


def make_context(base_dir: Path) -> RuntimeContext:
    """Create a RuntimeContext with a silent console pointed at tmp_path."""
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="1",  # Read + Write
        display_mode="standard",
        project_root=base_dir,
    )


def test_replace_command_usage(tmp_path):
    context = make_context(tmp_path)
    result = ReplaceCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Usage: /replace <path> <old_text> <new_text>" in output


def test_replace_command_success(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello world", encoding="utf-8")
    context = make_context(tmp_path)

    result = ReplaceCommand.execute(("test.txt", "world", "everyone"), context)
    assert result == CommandStatus.HANDLED
    assert file_path.read_text(encoding="utf-8") == "hello everyone"
    output = context.console.file.getvalue()
    assert "Replaced 1 occurrence(s)" in output


def test_replace_command_multiple(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("aaa bbb aaa", encoding="utf-8")
    context = make_context(tmp_path)

    result = ReplaceCommand.execute(("test.txt", "aaa", "ccc"), context)
    assert result == CommandStatus.HANDLED
    assert file_path.read_text(encoding="utf-8") == "ccc bbb ccc"
    output = context.console.file.getvalue()
    assert "Replaced 2 occurrence(s)" in output


def test_replace_command_no_matches(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello world", encoding="utf-8")
    context = make_context(tmp_path)

    result = ReplaceCommand.execute(("test.txt", "missing", "text"), context)
    assert result == CommandStatus.HANDLED
    assert file_path.read_text(encoding="utf-8") == "hello world"
    output = context.console.file.getvalue()
    assert "No matches found" in output


def test_replace_command_file_not_found(tmp_path):
    context = make_context(tmp_path)
    result = ReplaceCommand.execute(("nonexistent.txt", "old", "new"), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Error: File not found: nonexistent.txt" in output


def test_replace_command_escape_project_root_fails(tmp_path):
    context = make_context(tmp_path)
    escaped_path = "../../escaped.txt"

    result = ReplaceCommand.execute((escaped_path, "old", "new"), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Error: Access denied: path" in output


def test_replace_command_ignored_directory_fails(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("some config", encoding="utf-8")
    context = make_context(tmp_path)

    result = ReplaceCommand.execute((".git/config", "some", "other"), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Error: Access denied: path" in output
    assert (tmp_path / ".git" / "config").read_text(encoding="utf-8") == "some config"


# ---------------------------------------------------------------------------
# Command Routing & End-to-End Test
# ---------------------------------------------------------------------------

def test_replace_command_routing_and_e2e(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello standard user", encoding="utf-8")
    context = make_context(tmp_path)

    # Route /replace command end-to-end
    result = CommandRouter.route("/replace test.txt standard premium", context)
    assert result == CommandStatus.HANDLED

    # Verify output console message
    output = context.console.file.getvalue()
    assert "Replaced 1 occurrence(s)" in output

    # Verify actual file mutation on disk
    assert file_path.read_text(encoding="utf-8") == "hello premium user"
