import io
from pathlib import Path

import pytest
from rich.console import Console

from commands.largest_command import LargestCommand
from core.models import CommandStatus, RuntimeContext


def make_context(base_dir: Path) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="1",
        display_mode="standard",
        project_root=base_dir,
    )


def test_largest_default_limit(tmp_path):
    # Create 12 files
    for i in range(12):
        (tmp_path / f"file_{i}.txt").write_text("a" * (i + 1))

    context = make_context(tmp_path)
    result = LargestCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    
    output = context.console.file.getvalue()
    lines = [line for line in output.splitlines() if line.strip()]
    # Default limit is 10, so we should see exactly 10 printed lines
    assert len(lines) == 10
    assert "file_11.txt" in lines[0]  # Largest (12 bytes) first


def test_largest_custom_limit(tmp_path):
    for i in range(5):
        (tmp_path / f"file_{i}.txt").write_text("a" * (i + 1))

    context = make_context(tmp_path)
    result = LargestCommand.execute(("3",), context)
    assert result == CommandStatus.HANDLED
    
    output = context.console.file.getvalue()
    lines = [line for line in output.splitlines() if line.strip()]
    assert len(lines) == 3
    assert "file_4.txt" in lines[0]


def test_largest_invalid_limit(tmp_path):
    context = make_context(tmp_path)
    result = LargestCommand.execute(("abc",), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    assert "Usage: /largest [limit]" in output

    result_negative = LargestCommand.execute(("-5",), context)
    assert result_negative == CommandStatus.HANDLED
    output_negative = context.console.file.getvalue()
    assert "Limit must be a positive integer" in output_negative
