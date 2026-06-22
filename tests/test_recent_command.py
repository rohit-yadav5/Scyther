import io
import os
import time
from pathlib import Path

import pytest
from rich.console import Console

from scyther.commands.recent_command import RecentCommand
from scyther.core.models import CommandStatus, RuntimeContext


def make_context(base_dir: Path) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False),
        current_permission="1",
        display_mode="standard",
        project_root=base_dir,
    )


def test_recent_command_sorting_and_limits(tmp_path):
    f1 = tmp_path / "first.txt"
    f1.write_text("1")
    os.utime(f1, (time.time() - 10, time.time() - 10))

    f2 = tmp_path / "second.txt"
    f2.write_text("2")
    os.utime(f2, (time.time() - 5, time.time() - 5))

    f3 = tmp_path / "third.txt"
    f3.write_text("3")
    os.utime(f3, (time.time(), time.time()))

    context = make_context(tmp_path)
    result = RecentCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()

    assert output.index("third.txt") < output.index("second.txt")
    assert output.index("second.txt") < output.index("first.txt")


def test_recent_command_limit(tmp_path):
    for i in range(5):
        f = tmp_path / f"file_{i}.txt"
        f.write_text("content")
        os.utime(f, (time.time() - i, time.time() - i))

    context = make_context(tmp_path)
    result = RecentCommand.execute(("3",), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()

    assert "file_0.txt" in output
    assert "file_1.txt" in output
    assert "file_2.txt" in output
    assert "file_3.txt" not in output


def test_recent_command_ignores_venv_and_git(tmp_path):
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "lib.txt").write_text("some lib content")

    context = make_context(tmp_path)
    result = RecentCommand.execute((), context)
    assert result == CommandStatus.HANDLED
    output = context.console.file.getvalue()
    
    assert ".venv/lib.txt" not in output
