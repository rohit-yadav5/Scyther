import io
from pathlib import Path

import pytest
from rich.console import Console

from scyther.commands.create_command import CreateCommand
from scyther.commands.mkdir_command import MkdirCommand
from scyther.commands.write_command import WriteCommand
from scyther.commands.append_command import AppendCommand
from scyther.core.models import CommandStatus, RuntimeContext
from scyther.routing.command_router import CommandRouter


def make_context(base_dir: Path) -> RuntimeContext:
    """Create a RuntimeContext with a silent console pointed at tmp_path."""
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="1", # Read + Write
        display_mode="standard",
        project_root=base_dir,
    )


# ---------------------------------------------------------------------------
# /create command
# ---------------------------------------------------------------------------

def test_create_command_usage(tmp_path):
    context = make_context(tmp_path)
    result = CreateCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Usage: /create <path>" in output


def test_create_command_success(tmp_path):
    context = make_context(tmp_path)
    result = CreateCommand.execute(("new_file.txt",), context)
    assert result == CommandStatus.HANDLED
    assert (tmp_path / "new_file.txt").exists()
    assert (tmp_path / "new_file.txt").read_text() == ""
    output = context.console.file.getvalue()
    assert "Created empty file: new_file.txt" in output


def test_create_command_nested(tmp_path):
    context = make_context(tmp_path)
    result = CreateCommand.execute(("nested/dir/new_file.txt",), context)
    assert result == CommandStatus.HANDLED
    assert (tmp_path / "nested" / "dir" / "new_file.txt").exists()
    assert (tmp_path / "nested" / "dir" / "new_file.txt").read_text() == ""
    output = context.console.file.getvalue()
    assert "Created empty file: nested/dir/new_file.txt" in output


def test_create_command_already_exists_fails(tmp_path):
    (tmp_path / "existing.txt").write_text("hello")
    context = make_context(tmp_path)
    result = CreateCommand.execute(("existing.txt",), context)
    assert result == CommandStatus.HANDLED
    # File content should not have been cleared
    assert (tmp_path / "existing.txt").read_text() == "hello"
    output = context.console.file.getvalue()
    assert "Error: File already exists: existing.txt" in output


# ---------------------------------------------------------------------------
# /mkdir command
# ---------------------------------------------------------------------------

def test_mkdir_command_usage(tmp_path):
    context = make_context(tmp_path)
    result = MkdirCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Usage: /mkdir <path>" in output


def test_mkdir_command_success(tmp_path):
    context = make_context(tmp_path)
    result = MkdirCommand.execute(("new_dir",), context)
    assert result == CommandStatus.HANDLED
    assert (tmp_path / "new_dir").is_dir()
    output = context.console.file.getvalue()
    assert "Created directory: new_dir" in output


def test_mkdir_command_nested(tmp_path):
    context = make_context(tmp_path)
    result = MkdirCommand.execute(("nested/dir/new_dir",), context)
    assert result == CommandStatus.HANDLED
    assert (tmp_path / "nested" / "dir" / "new_dir").is_dir()
    output = context.console.file.getvalue()
    assert "Created directory: nested/dir/new_dir" in output


def test_mkdir_command_already_exists_fails(tmp_path):
    (tmp_path / "existing_dir").mkdir()
    context = make_context(tmp_path)
    result = MkdirCommand.execute(("existing_dir",), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Error: Path already exists: existing_dir" in output


# ---------------------------------------------------------------------------
# /write command
# ---------------------------------------------------------------------------

def test_write_command_usage(tmp_path):
    context = make_context(tmp_path)
    result = WriteCommand.execute(("only_path",), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Usage: /write <path> <content>" in output


def test_write_command_creates_new_file(tmp_path):
    context = make_context(tmp_path)
    result = WriteCommand.execute(("written.txt", "hello", "world"), context)
    assert result == CommandStatus.HANDLED
    assert (tmp_path / "written.txt").read_text() == "hello world"
    output = context.console.file.getvalue()
    assert "Wrote to file: written.txt" in output


def test_write_command_overwrites_existing_file(tmp_path):
    (tmp_path / "written.txt").write_text("old content")
    context = make_context(tmp_path)
    result = WriteCommand.execute(("written.txt", "new", "content"), context)
    assert result == CommandStatus.HANDLED
    assert (tmp_path / "written.txt").read_text() == "new content"
    output = context.console.file.getvalue()
    assert "Wrote to file: written.txt" in output


def test_write_to_directory_fails(tmp_path):
    (tmp_path / "some_dir").mkdir()
    context = make_context(tmp_path)
    result = WriteCommand.execute(("some_dir", "content"), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Error: Cannot write to a directory: some_dir" in output


# ---------------------------------------------------------------------------
# /append command
# ---------------------------------------------------------------------------

def test_append_command_usage(tmp_path):
    context = make_context(tmp_path)
    result = AppendCommand.execute(("only_path",), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Usage: /append <path> <content>" in output


def test_append_creates_file_if_not_exists(tmp_path):
    context = make_context(tmp_path)
    result = AppendCommand.execute(("appended.txt", "hello"), context)
    assert result == CommandStatus.HANDLED
    assert (tmp_path / "appended.txt").read_text() == "hello"


def test_append_appends_to_existing_file(tmp_path):
    (tmp_path / "appended.txt").write_text("hello ")
    context = make_context(tmp_path)
    result = AppendCommand.execute(("appended.txt", "world", "!"), context)
    assert result == CommandStatus.HANDLED
    assert (tmp_path / "appended.txt").read_text() == "hello world !"
    output = context.console.file.getvalue()
    assert "Appended to file: appended.txt" in output


# ---------------------------------------------------------------------------
# Boundary & IGNORED_DIRS tests (Security boundary checks)
# ---------------------------------------------------------------------------

def test_mutation_outside_project_root_fails(tmp_path):
    context = make_context(tmp_path)
    # Target outside project root
    escaped_path = "../../escaped.txt"

    # Test /create
    result = CreateCommand.execute((escaped_path,), context)
    assert result == CommandStatus.HANDLED
    assert "Error: Access denied: path" in context.console.file.getvalue()
    assert not (tmp_path.parent / "escaped.txt").exists()

    # Test /mkdir
    context.console.file = io.StringIO()
    result = MkdirCommand.execute((escaped_path,), context)
    assert result == CommandStatus.HANDLED
    assert "Error: Access denied: path" in context.console.file.getvalue()

    # Test /write
    context.console.file = io.StringIO()
    result = WriteCommand.execute((escaped_path, "content"), context)
    assert result == CommandStatus.HANDLED
    assert "Error: Access denied: path" in context.console.file.getvalue()

    # Test /append
    context.console.file = io.StringIO()
    result = AppendCommand.execute((escaped_path, "content"), context)
    assert result == CommandStatus.HANDLED
    assert "Error: Access denied: path" in context.console.file.getvalue()


def test_mutation_in_ignored_directory_fails(tmp_path):
    # Setup venv and git dirs
    (tmp_path / ".git").mkdir()
    (tmp_path / ".venv").mkdir()

    context = make_context(tmp_path)

    # Test /create in .git
    result = CreateCommand.execute((".git/some_file.txt",), context)
    assert result == CommandStatus.HANDLED
    assert "Error: Access denied: path" in context.console.file.getvalue()
    assert not (tmp_path / ".git" / "some_file.txt").exists()

    # Test /mkdir in .venv
    context.console.file = io.StringIO()
    result = MkdirCommand.execute((".venv/new_sub_dir",), context)
    assert result == CommandStatus.HANDLED
    assert "Error: Access denied: path" in context.console.file.getvalue()
    assert not (tmp_path / ".venv" / "new_sub_dir").exists()


# ---------------------------------------------------------------------------
# Command Routing tests
# ---------------------------------------------------------------------------

def test_command_routing_for_mutations(tmp_path):
    context = make_context(tmp_path)

    # Route /create
    assert CommandRouter.route("/create routed_file.txt", context) == CommandStatus.HANDLED
    assert (tmp_path / "routed_file.txt").exists()

    # Route /write
    assert CommandRouter.route("/write routed_file.txt hello", context) == CommandStatus.HANDLED
    assert (tmp_path / "routed_file.txt").read_text() == "hello"

    # Route /append
    assert CommandRouter.route("/append routed_file.txt world", context) == CommandStatus.HANDLED
    assert (tmp_path / "routed_file.txt").read_text() == "helloworld"

    # Route /mkdir
    assert CommandRouter.route("/mkdir routed_dir", context) == CommandStatus.HANDLED
    assert (tmp_path / "routed_dir").is_dir()
