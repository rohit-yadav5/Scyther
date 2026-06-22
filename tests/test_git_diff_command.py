import io
from pathlib import Path

import pytest
from rich.console import Console

from scyther.commands.git_diff_command import GitDiffCommand
from scyther.core.models import CommandStatus, RuntimeContext
from scyther.tools.git_tool import GitTool


def make_context(base_dir: Path) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="1",
        display_mode="standard",
        project_root=base_dir,
    )


def test_git_diff_command_success(monkeypatch, tmp_path):
    (tmp_path / ".git").mkdir()
    monkeypatch.setattr(GitTool, "is_git_repository", lambda cwd: True)
    monkeypatch.setattr(GitTool, "git_diff", lambda cwd: "diff --git a/file.py b/file.py\n+new line")

    context = make_context(tmp_path)
    result = GitDiffCommand.execute((), context)

    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "diff --git a/file.py" in output
    assert "+new line" in output


def test_git_diff_command_no_changes(monkeypatch, tmp_path):
    (tmp_path / ".git").mkdir()
    monkeypatch.setattr(GitTool, "is_git_repository", lambda cwd: True)
    monkeypatch.setattr(GitTool, "git_diff", lambda cwd: "")

    context = make_context(tmp_path)
    result = GitDiffCommand.execute((), context)

    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "No changes in working tree." in output


def test_git_diff_command_truncation(monkeypatch, tmp_path):
    (tmp_path / ".git").mkdir()
    monkeypatch.setattr(GitTool, "is_git_repository", lambda cwd: True)
    
    # Generate 550 lines of diff
    large_diff = "\n".join(f"line {i}" for i in range(550))
    monkeypatch.setattr(GitTool, "git_diff", lambda cwd: large_diff)

    context = make_context(tmp_path)
    result = GitDiffCommand.execute((), context)

    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    
    assert "line 499" in output
    assert "line 501" not in output
    assert "Warning: Diff output truncated to first 500 lines." in output


def test_git_diff_command_not_a_repo(monkeypatch, tmp_path):
    context = make_context(tmp_path)
    result = GitDiffCommand.execute((), context)

    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Error: Current project is not a git repository." in output
