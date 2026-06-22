import io
from pathlib import Path

import pytest
from rich.console import Console

from scyther.commands.search_command import SearchCommand
from scyther.core.models import CommandStatus, RuntimeContext


def make_context(base_dir: Path) -> RuntimeContext:
    """Create a RuntimeContext with a silent console pointed at tmp_path."""
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="3",
        display_mode="standard",
        project_root=base_dir,
    )


def build_search_repo(root: Path) -> None:
    """Populate a test project root with files containing search patterns."""
    (root / "permissions").mkdir()
    (root / "permissions" / "permission_manager.py").write_text(
        "class PermissionManager:\n    def set_permission(self):\n        pass\n",
        encoding="utf-8"
    )
    (root / "services").mkdir()
    (root / "services" / "file_service.py").write_text(
        "from permissions.permission_manager import PermissionManager\n",
        encoding="utf-8"
    )
    (root / "core").mkdir()
    (root / "core" / "models.py").write_text(
        "class RuntimeContext:\n    pass\n",
        encoding="utf-8"
    )


def test_search_command_usage_no_args(tmp_path):
    context = make_context(tmp_path)
    result = SearchCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Usage: /search <pattern>" in output


def test_search_command_finds_permission_manager(tmp_path):
    build_search_repo(tmp_path)
    context = make_context(tmp_path)

    # Search for "PermissionManager" (exact case)
    result = SearchCommand.execute(("PermissionManager",), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()

    assert "Found 2 matches" in output
    assert "permissions/permission_manager.py:1" in output
    assert "services/file_service.py:1" in output


def test_search_command_is_case_insensitive(tmp_path):
    build_search_repo(tmp_path)
    context = make_context(tmp_path)

    # Search case-insensitively for "permissionmanager"
    result = SearchCommand.execute(("permissionmanager",), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()

    assert "Found 2 matches" in output
    assert "permissions/permission_manager.py:1" in output
    assert "services/file_service.py:1" in output


def test_search_command_finds_runtime_context(tmp_path):
    build_search_repo(tmp_path)
    context = make_context(tmp_path)

    result = SearchCommand.execute(("RuntimeContext",), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()

    assert "Found 1 matches" in output
    assert "core/models.py:1" in output


def test_search_command_missing_text(tmp_path):
    build_search_repo(tmp_path)
    context = make_context(tmp_path)

    result = SearchCommand.execute(("missing_text",), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()

    assert "Found 0 matches" in output
    # Should not print any file path or matches
    assert "permissions" not in output
