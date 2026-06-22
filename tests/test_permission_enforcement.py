import io
import builtins
from pathlib import Path

import pytest
from rich.console import Console

from core.models import CommandStatus, RuntimeContext
from routing.command_router import CommandRouter


def make_context(base_dir: Path, permission: str) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission=permission,
        display_mode="standard",
        project_root=base_dir,
    )


def test_read_only_blocks_mutations(tmp_path):
    # Set to Read Only (3)
    context = make_context(tmp_path, "3")
    
    res = CommandRouter.route("/create foo.txt", context)
    assert res == CommandStatus.HANDLED
    assert not (tmp_path / "foo.txt").exists()
    
    output = context.console.file.getvalue()
    assert "Permission denied." in output
    assert "Current mode: Read Only" in output


def test_ask_before_edit_denied(tmp_path, monkeypatch):
    # Set to Ask Before Edit (2)
    context = make_context(tmp_path, "2")
    
    # Mock input to return 'n' (reject)
    monkeypatch.setattr(builtins, "input", lambda prompt="": "n")
    
    res = CommandRouter.route("/create foo.txt", context)
    assert res == CommandStatus.HANDLED
    assert not (tmp_path / "foo.txt").exists()
    
    output = context.console.file.getvalue()
    assert "You are about to execute:" in output
    assert "/create foo.txt" in output


def test_ask_before_edit_approved(tmp_path, monkeypatch):
    # Set to Ask Before Edit (2)
    context = make_context(tmp_path, "2")
    
    # Mock input to return 'y' (approve)
    monkeypatch.setattr(builtins, "input", lambda prompt="": "y")
    
    res = CommandRouter.route("/create foo.txt", context)
    assert res == CommandStatus.HANDLED
    assert (tmp_path / "foo.txt").exists()


def test_full_access_executes_immediately(tmp_path):
    # Set to Full Access (1)
    context = make_context(tmp_path, "1")
    
    res = CommandRouter.route("/create foo.txt", context)
    assert res == CommandStatus.HANDLED
    assert (tmp_path / "foo.txt").exists()


def test_all_mutation_commands_enforced(tmp_path):
    # Verify that all 8 mutation commands are blocked under Read Only mode
    mutations = [
        "/create foo.txt",
        "/mkdir sub",
        "/write foo.txt hello",
        "/append foo.txt world",
        "/replace foo.txt hello world",
        "/delete foo.txt",
        "/move foo.txt bar.txt",
        "/copy foo.txt bar.txt",
    ]
    
    for cmd in mutations:
        context = make_context(tmp_path, "3")
        res = CommandRouter.route(cmd, context)
        assert res == CommandStatus.HANDLED
        output = context.console.file.getvalue()
        assert "Permission denied." in output
        assert "Current mode: Read Only" in output
