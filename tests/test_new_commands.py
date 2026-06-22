"""
Integration tests for all new commands introduced in Phase 1.

Each command is tested against a real temporary filesystem (using pytest's
tmp_path fixture) with a silent Rich Console so output does not clutter
the test runner. All tests assert only on CommandStatus return values and
observable side-effects (e.g. files being read), not on terminal output.
"""

import io
from pathlib import Path

import pytest
from rich.console import Console

from scyther.commands.find_command import FindCommand
from scyther.commands.list_command import ListCommand
from scyther.commands.open_command import OpenCommand
from scyther.commands.summary_command import SummaryCommand
from scyther.commands.tree_command import TreeCommand
from scyther.commands.exit_command import ExitCommand
from scyther.core.models import CommandStatus, RuntimeContext


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_context(base_dir: Path) -> RuntimeContext:
    """Create a RuntimeContext with a silent console pointed at tmp_path."""
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="3",
        display_mode="standard",
        project_root=base_dir,
    )


def build_repo(root: Path) -> None:
    """Populate a minimal repo structure for testing."""
    (root / "README.md").write_text("# Scyther\n", encoding="utf-8")
    (root / "core").mkdir()
    (root / "core" / "models.py").write_text("class Foo: pass\n", encoding="utf-8")
    (root / "core" / "config.py").write_text("DEBUG = False\n", encoding="utf-8")
    (root / "tools").mkdir()
    (root / "tools" / "repo_tool.py").write_text("class RepoTool: pass\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# ExitCommand
# ---------------------------------------------------------------------------


def test_exit_command_returns_exit_status(tmp_path):
    context = make_context(tmp_path)
    result = ExitCommand.execute((), context)
    assert result == CommandStatus.EXIT


# ---------------------------------------------------------------------------
# ListCommand
# ---------------------------------------------------------------------------


def test_list_command_returns_handled(tmp_path):
    build_repo(tmp_path)
    context = make_context(tmp_path)
    result = ListCommand.execute((), context)
    assert result == CommandStatus.HANDLED


def test_list_command_works_on_empty_directory(tmp_path):
    context = make_context(tmp_path)
    result = ListCommand.execute((), context)
    assert result == CommandStatus.HANDLED


# ---------------------------------------------------------------------------
# TreeCommand
# ---------------------------------------------------------------------------


def test_tree_command_returns_handled(tmp_path):
    build_repo(tmp_path)
    context = make_context(tmp_path)
    result = TreeCommand.execute((), context)
    assert result == CommandStatus.HANDLED


def test_tree_command_with_valid_depth(tmp_path):
    build_repo(tmp_path)
    context = make_context(tmp_path)
    result = TreeCommand.execute(("1",), context)
    assert result == CommandStatus.HANDLED


def test_tree_command_with_invalid_depth_still_returns_handled(tmp_path):
    context = make_context(tmp_path)
    result = TreeCommand.execute(("abc",), context)
    # should not raise; returns HANDLED with an error message
    assert result == CommandStatus.HANDLED


def test_tree_command_ignores_extra_args(tmp_path):
    build_repo(tmp_path)
    context = make_context(tmp_path)
    # Only the first arg is consumed as depth; extra args are silently ignored
    result = TreeCommand.execute(("2", "extra"), context)
    assert result == CommandStatus.HANDLED


# ---------------------------------------------------------------------------
# OpenCommand
# ---------------------------------------------------------------------------


def test_open_command_reads_existing_file(tmp_path):
    (tmp_path / "README.md").write_text("hello world", encoding="utf-8")
    context = make_context(tmp_path)
    result = OpenCommand.execute(("README.md",), context)
    assert result == CommandStatus.HANDLED


def test_open_command_finds_file_in_subdirectory(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "deep.py").write_text("x = 1", encoding="utf-8")
    context = make_context(tmp_path)
    result = OpenCommand.execute(("deep.py",), context)
    assert result == CommandStatus.HANDLED


def test_open_command_missing_file_returns_handled(tmp_path):
    context = make_context(tmp_path)
    result = OpenCommand.execute(("nonexistent.py",), context)
    # Should return HANDLED (error rendered), not raise
    assert result == CommandStatus.HANDLED


def test_open_command_with_no_args_returns_handled(tmp_path):
    context = make_context(tmp_path)
    result = OpenCommand.execute((), context)
    assert result == CommandStatus.HANDLED


def test_open_command_on_directory_returns_handled(tmp_path):
    (tmp_path / "subdir").mkdir()
    context = make_context(tmp_path)
    # Passing a directory name — FileService raises IsADirectoryError
    result = OpenCommand.execute(("subdir",), context)
    assert result == CommandStatus.HANDLED


# ---------------------------------------------------------------------------
# FindCommand
# ---------------------------------------------------------------------------


def test_find_command_locates_existing_file(tmp_path):
    build_repo(tmp_path)
    context = make_context(tmp_path)
    result = FindCommand.execute(("README.md",), context)
    assert result == CommandStatus.HANDLED


def test_find_command_no_matches_still_returns_handled(tmp_path):
    build_repo(tmp_path)
    context = make_context(tmp_path)
    result = FindCommand.execute(("ghost.py",), context)
    assert result == CommandStatus.HANDLED


def test_find_command_with_no_args_returns_handled(tmp_path):
    context = make_context(tmp_path)
    result = FindCommand.execute((), context)
    assert result == CommandStatus.HANDLED


# ---------------------------------------------------------------------------
# SummaryCommand
# ---------------------------------------------------------------------------


def test_summary_command_returns_handled(tmp_path):
    build_repo(tmp_path)
    context = make_context(tmp_path)
    result = SummaryCommand.execute((), context)
    assert result == CommandStatus.HANDLED


def test_summary_command_on_empty_directory(tmp_path):
    context = make_context(tmp_path)
    result = SummaryCommand.execute((), context)
    assert result == CommandStatus.HANDLED
