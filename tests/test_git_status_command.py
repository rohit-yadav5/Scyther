import io
from pathlib import Path

import pytest
from rich.console import Console

from scyther.commands.git_status_command import GitStatusCommand
from scyther.core.models import CommandStatus, RuntimeContext
from scyther.tools.git_tool import GitTool


def make_context(base_dir: Path) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="1",
        display_mode="standard",
        project_root=base_dir,
    )


def test_git_status_command_success(monkeypatch, tmp_path):
    # Setup mock .git folder
    (tmp_path / ".git").mkdir()

    # Mock GitTool methods
    monkeypatch.setattr(GitTool, "is_git_repository", lambda cwd: True)
    monkeypatch.setattr(GitTool, "git_status", lambda cwd: "M services/file_service.py\n?? temp.txt")

    context = make_context(tmp_path)
    result = GitStatusCommand.execute((), context)

    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "M services/file_service.py" in output
    assert "?? temp.txt" in output


def test_git_status_command_not_a_repo(monkeypatch, tmp_path):
    context = make_context(tmp_path)
    result = GitStatusCommand.execute((), context)

    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Error: Current project is not a git repository." in output


def test_git_status_command_clean_working_tree(monkeypatch, tmp_path):
    (tmp_path / ".git").mkdir()
    monkeypatch.setattr(GitTool, "is_git_repository", lambda cwd: True)
    monkeypatch.setattr(GitTool, "git_status", lambda cwd: "")

    context = make_context(tmp_path)
    result = GitStatusCommand.execute((), context)

    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Working tree clean." in output
