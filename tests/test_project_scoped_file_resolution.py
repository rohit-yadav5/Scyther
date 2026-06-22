"""
Phase 3 safety tests — project-scoped file resolution.

Covers:
  - FileService: direct path, rglob, ignored dirs, multiple matches,
    project-root boundary enforcement.
  - RepoTool: tree/find ignore .git, .venv, __pycache__, .pytest_cache.
  - Command layer: OpenCommand, FindCommand multi-match UX.
  - Regression suite: all 9 commands return the correct CommandStatus.
"""

import io
from pathlib import Path

import pytest
from rich.console import Console

from commands.display_command import DisplayCommand
from commands.exit_command import ExitCommand
from commands.find_command import FindCommand
from commands.help_command import HelpCommand
from commands.list_command import ListCommand
from commands.open_command import OpenCommand
from commands.permission_command import PermissionCommand
from commands.summary_command import SummaryCommand
from commands.tree_command import TreeCommand
from core.models import CommandStatus, MultipleMatchesError, RuntimeContext
from routing.command_router import CommandRouter
from services.file_service import FileService
from tools.repo_tool import RepoTool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_context(root: Path) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="3",
        display_mode="standard",
        project_root=root,
    )


def build_project(root: Path) -> None:
    """Minimal project layout: README + src/main.py + tests/test_main.py."""
    (root / "README.md").write_text("# Project\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "main.py").write_text("def main(): pass\n", encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests" / "test_main.py").write_text("import main\n", encoding="utf-8")


def add_ignored_dirs(root: Path) -> None:
    """Simulate ignored directories that exist inside a real project."""
    (root / ".git").mkdir()
    (root / ".git" / "config").write_text("[core]", encoding="utf-8")

    (root / ".venv").mkdir()
    (root / ".venv" / "lib").mkdir()
    (root / ".venv" / "lib" / "main.py").write_text("venv code", encoding="utf-8")

    (root / "__pycache__").mkdir()
    (root / "__pycache__" / "main.cpython-313.pyc").write_bytes(b"\x00bytecode")

    (root / ".pytest_cache").mkdir()
    (root / ".pytest_cache" / "README.md").write_text("pytest cache", encoding="utf-8")


# ---------------------------------------------------------------------------
# FileService — project root enforcement
# ---------------------------------------------------------------------------


class TestFileServiceSafety:
    def test_read_file_by_name(self, tmp_path):
        build_project(tmp_path)
        service = FileService(str(tmp_path))
        result = service.read_file("README.md")
        assert result["content"] == "# Project\n"
        assert result["path"] == "README.md"

    def test_read_file_in_subdirectory_by_name(self, tmp_path):
        build_project(tmp_path)
        service = FileService(str(tmp_path))
        result = service.read_file("main.py")
        assert result["path"] == "src/main.py"

    def test_read_file_by_relative_path(self, tmp_path):
        build_project(tmp_path)
        service = FileService(str(tmp_path))
        result = service.read_file("src/main.py")
        assert result["path"] == "src/main.py"
        assert "def main" in result["content"]

    def test_missing_file_raises_not_found(self, tmp_path):
        service = FileService(str(tmp_path))
        with pytest.raises(FileNotFoundError, match="File not found: missing.py"):
            service.read_file("missing.py")

    def test_venv_file_is_not_found_when_only_in_venv(self, tmp_path):
        """main.py exists only inside .venv — FileService must not surface it."""
        add_ignored_dirs(tmp_path)
        # No main.py in the actual project
        service = FileService(str(tmp_path))
        with pytest.raises(FileNotFoundError):
            service.read_file("main.py")

    def test_project_file_wins_over_venv_duplicate(self, tmp_path):
        """main.py in both project and .venv — only the project copy is returned."""
        add_ignored_dirs(tmp_path)  # .venv/lib/main.py exists
        (tmp_path / "src").mkdir(exist_ok=True)
        (tmp_path / "src" / "main.py").write_text("project code", encoding="utf-8")
        service = FileService(str(tmp_path))
        result = service.read_file("main.py")
        assert result["content"] == "project code"
        assert ".venv" not in result["path"]

    def test_pytest_cache_readme_is_not_returned(self, tmp_path):
        """README.md inside .pytest_cache must not shadow the project README."""
        build_project(tmp_path)
        add_ignored_dirs(tmp_path)  # .pytest_cache/README.md also exists
        service = FileService(str(tmp_path))
        result = service.read_file("README.md")
        assert result["path"] == "README.md"
        assert result["content"] == "# Project\n"

    def test_multiple_matches_raises_error(self, tmp_path):
        """Two files with the same name in different dirs raises MultipleMatchesError."""
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "src" / "utils.py").write_text("src", encoding="utf-8")
        (tmp_path / "tests" / "utils.py").write_text("tests", encoding="utf-8")
        service = FileService(str(tmp_path))
        with pytest.raises(MultipleMatchesError) as exc_info:
            service.read_file("utils.py")
        matches = exc_info.value.matches
        assert any("src/utils.py" in m for m in matches)
        assert any("tests/utils.py" in m for m in matches)
        assert exc_info.value.filename == "utils.py"

    def test_multiple_matches_excludes_ignored_dirs(self, tmp_path):
        """Identical filename in project and .venv — only project match counts."""
        add_ignored_dirs(tmp_path)  # .venv/lib/main.py
        (tmp_path / "src").mkdir(exist_ok=True)
        (tmp_path / "src" / "main.py").write_text("only match", encoding="utf-8")
        service = FileService(str(tmp_path))
        # Only one project-side match → no MultipleMatchesError
        result = service.read_file("main.py")
        assert result["content"] == "only match"


# ---------------------------------------------------------------------------
# RepoTool — ignored directory filtering
# ---------------------------------------------------------------------------


class TestRepoToolSafety:
    def test_tree_files_excludes_git(self, tmp_path):
        build_project(tmp_path)
        add_ignored_dirs(tmp_path)
        tree = RepoTool.tree(str(tmp_path))
        assert all(not f.startswith(".git") for f in tree["files"])
        assert all(not d.startswith(".git") for d in tree["directories"])

    def test_tree_files_excludes_venv(self, tmp_path):
        build_project(tmp_path)
        add_ignored_dirs(tmp_path)
        tree = RepoTool.tree(str(tmp_path))
        assert all(".venv" not in f for f in tree["files"])

    def test_tree_files_excludes_pycache(self, tmp_path):
        build_project(tmp_path)
        add_ignored_dirs(tmp_path)
        tree = RepoTool.tree(str(tmp_path))
        assert all("__pycache__" not in f for f in tree["files"])

    def test_tree_files_excludes_pytest_cache(self, tmp_path):
        build_project(tmp_path)
        add_ignored_dirs(tmp_path)
        tree = RepoTool.tree(str(tmp_path))
        assert all(".pytest_cache" not in f for f in tree["files"])

    def test_tree_contains_all_project_files(self, tmp_path):
        build_project(tmp_path)
        add_ignored_dirs(tmp_path)
        tree = RepoTool.tree(str(tmp_path))
        assert "README.md" in tree["files"]
        assert "src/main.py" in tree["files"]
        assert "tests/test_main.py" in tree["files"]

    def test_tree_directories_populated_correctly(self, tmp_path):
        build_project(tmp_path)
        add_ignored_dirs(tmp_path)
        tree = RepoTool.tree(str(tmp_path))
        assert "src" in tree["directories"]
        assert "tests" in tree["directories"]

    def test_find_ignores_venv(self, tmp_path):
        add_ignored_dirs(tmp_path)  # .venv/lib/main.py
        matches = RepoTool.find_file(str(tmp_path), "main.py")
        assert matches == []

    def test_find_locates_project_file(self, tmp_path):
        build_project(tmp_path)
        add_ignored_dirs(tmp_path)
        matches = RepoTool.find_file(str(tmp_path), "main.py")
        assert matches == ["src/main.py"]

    def test_list_files_excludes_ignored(self, tmp_path):
        build_project(tmp_path)
        add_ignored_dirs(tmp_path)
        files = RepoTool.list_files(str(tmp_path))
        assert all(".venv" not in f for f in files)
        assert all(".git" not in f for f in files)
        assert all("__pycache__" not in f for f in files)


# ---------------------------------------------------------------------------
# OpenCommand — multiple match UX
# ---------------------------------------------------------------------------


class TestOpenCommandSafety:
    def test_open_single_match(self, tmp_path):
        build_project(tmp_path)
        context = make_context(tmp_path)
        result = OpenCommand.execute(("README.md",), context)
        assert result == CommandStatus.HANDLED

    def test_open_missing_file(self, tmp_path):
        context = make_context(tmp_path)
        result = OpenCommand.execute(("missing.py",), context)
        assert result == CommandStatus.HANDLED

    def test_open_multiple_matches_returns_handled(self, tmp_path):
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "src" / "utils.py").write_text("src", encoding="utf-8")
        (tmp_path / "tests" / "utils.py").write_text("tests", encoding="utf-8")
        context = make_context(tmp_path)
        result = OpenCommand.execute(("utils.py",), context)
        # Must return HANDLED (listing candidates), not raise
        assert result == CommandStatus.HANDLED

    def test_open_no_args(self, tmp_path):
        context = make_context(tmp_path)
        result = OpenCommand.execute((), context)
        assert result == CommandStatus.HANDLED

    def test_open_file_only_in_venv_returns_not_found(self, tmp_path):
        add_ignored_dirs(tmp_path)
        context = make_context(tmp_path)
        result = OpenCommand.execute(("main.py",), context)
        # File exists only in .venv → not found → HANDLED with error message
        assert result == CommandStatus.HANDLED

    def test_open_full_relative_path(self, tmp_path):
        build_project(tmp_path)
        context = make_context(tmp_path)
        result = OpenCommand.execute(("src/main.py",), context)
        assert result == CommandStatus.HANDLED


# ---------------------------------------------------------------------------
# FindCommand — project-scoped search
# ---------------------------------------------------------------------------


class TestFindCommandSafety:
    def test_find_existing_file(self, tmp_path):
        build_project(tmp_path)
        context = make_context(tmp_path)
        result = FindCommand.execute(("README.md",), context)
        assert result == CommandStatus.HANDLED

    def test_find_missing_file(self, tmp_path):
        context = make_context(tmp_path)
        result = FindCommand.execute(("ghost.py",), context)
        assert result == CommandStatus.HANDLED

    def test_find_does_not_return_venv_files(self, tmp_path):
        add_ignored_dirs(tmp_path)  # .venv/lib/main.py exists
        # No main.py in project → find should produce zero results (HANDLED)
        context = make_context(tmp_path)
        result = FindCommand.execute(("main.py",), context)
        assert result == CommandStatus.HANDLED


# ---------------------------------------------------------------------------
# Regression — all 9 commands return correct CommandStatus
# ---------------------------------------------------------------------------


class TestCommandRegression:
    def test_help(self, tmp_path):
        assert HelpCommand.execute((), make_context(tmp_path)) == CommandStatus.HANDLED

    def test_list(self, tmp_path):
        build_project(tmp_path)
        assert ListCommand.execute((), make_context(tmp_path)) == CommandStatus.HANDLED

    def test_tree(self, tmp_path):
        build_project(tmp_path)
        assert TreeCommand.execute((), make_context(tmp_path)) == CommandStatus.HANDLED

    def test_tree_with_depth(self, tmp_path):
        build_project(tmp_path)
        assert TreeCommand.execute(("2",), make_context(tmp_path)) == CommandStatus.HANDLED

    def test_open_readme(self, tmp_path):
        build_project(tmp_path)
        assert OpenCommand.execute(("README.md",), make_context(tmp_path)) == CommandStatus.HANDLED

    def test_find_readme(self, tmp_path):
        build_project(tmp_path)
        assert FindCommand.execute(("README.md",), make_context(tmp_path)) == CommandStatus.HANDLED

    def test_summary(self, tmp_path):
        build_project(tmp_path)
        assert SummaryCommand.execute((), make_context(tmp_path)) == CommandStatus.HANDLED

    def test_exit(self, tmp_path):
        assert ExitCommand.execute((), make_context(tmp_path)) == CommandStatus.EXIT

    def test_display_via_router(self, tmp_path, monkeypatch):
        monkeypatch.setattr(DisplayCommand, "execute", lambda args, ctx: CommandStatus.HANDLED)
        assert CommandRouter.route("/display", make_context(tmp_path)) == CommandStatus.HANDLED

    def test_permission_via_router(self, tmp_path, monkeypatch):
        monkeypatch.setattr(PermissionCommand, "execute", lambda args, ctx: CommandStatus.HANDLED)
        assert CommandRouter.route("/permission", make_context(tmp_path)) == CommandStatus.HANDLED

    def test_unknown_slash_command(self, tmp_path):
        assert CommandRouter.route("/unknown", make_context(tmp_path)) == CommandStatus.NOT_HANDLED

    def test_plain_text_is_not_handled(self, tmp_path):
        ctx = make_context(tmp_path)
        assert CommandRouter.route("show tree", ctx) == CommandStatus.NOT_HANDLED
        assert CommandRouter.route("open README.md", ctx) == CommandStatus.NOT_HANDLED
        assert CommandRouter.route("list files", ctx) == CommandStatus.NOT_HANDLED
        assert CommandRouter.route("tree", ctx) == CommandStatus.NOT_HANDLED
