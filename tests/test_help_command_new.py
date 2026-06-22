import io
from pathlib import Path

import pytest
from rich.console import Console

from scyther.commands.help_command import HelpCommand
from scyther.core.models import CommandStatus, RuntimeContext


def make_context(base_dir: Path) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="1",
        display_mode="standard",
        project_root=base_dir,
    )


def test_help_no_args(tmp_path):
    context = make_context(tmp_path)
    result = HelpCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    
    assert "Repository Commands" in output
    assert "Modification Commands" in output
    assert "Git Commands" in output
    assert "System Commands" in output
    assert "⚠ Dangerous" in output


def test_help_with_arg_no_slash(tmp_path):
    context = make_context(tmp_path)
    result = HelpCommand.execute(("delete",), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    
    assert "Command: /delete" in output
    assert "Usage:" in output
    assert "/delete [--force] <path>" in output
    assert "Dangerous:" in output
    assert "Yes" in output
    assert "Category:" in output
    assert "Modification" in output


def test_help_with_arg_with_slash(tmp_path):
    context = make_context(tmp_path)
    result = HelpCommand.execute(("/open",), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    
    assert "Command: /open" in output
    assert "Usage:" in output
    assert "/open <file>" in output
    assert "Dangerous:" in output
    assert "No" in output
    assert "Category:" in output
    assert "Repository" in output


def test_help_nonexistent(tmp_path):
    context = make_context(tmp_path)
    result = HelpCommand.execute(("ghost",), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    
    assert "No help available for command: /ghost" in output
