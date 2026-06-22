import io
from pathlib import Path

import pytest
from rich.console import Console

from commands.where_command import WhereCommand
from core.models import CommandStatus, RuntimeContext


def make_context(base_dir: Path) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="1",
        display_mode="standard",
        project_root=base_dir,
    )


def test_where_command_usage(tmp_path):
    context = make_context(tmp_path)
    result = WhereCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Usage: /where <symbol>" in output


def test_where_symbol_found(tmp_path):
    # Create Python file with definition
    (tmp_path / "service.py").write_text(
        "class OrderService:\n"
        "    pass\n",
        encoding="utf-8"
    )
    context = make_context(tmp_path)
    result = WhereCommand.execute(("OrderService",), context)
    assert result == CommandStatus.HANDLED
    
    output = context.console.file.getvalue()
    assert "Definition Found" in output
    assert "OrderService" in output
    assert "service.py:1" in output


def test_where_symbol_missing(tmp_path):
    context = make_context(tmp_path)
    result = WhereCommand.execute(("NonexistentService",), context)
    assert result == CommandStatus.HANDLED
    
    output = context.console.file.getvalue()
    assert "No definition found for 'NonexistentService'" in output
