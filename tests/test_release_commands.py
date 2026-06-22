import io
import sys
from pathlib import Path
import pytest
from rich.console import Console

from scyther.core.models import CommandStatus, RuntimeContext
from scyther.routing.command_router import CommandRouter
from scyther.commands.about_command import AboutCommand
from scyther.commands.version_command import VersionCommand
from scyther.commands.doctor_command import DoctorCommand
from scyther.commands.config_command import ConfigCommand
from scyther.core.version import __version__


def make_context(base_dir: Path) -> RuntimeContext:
    return RuntimeContext(
        console=Console(file=io.StringIO(), highlight=False, width=1000),
        current_permission="1",
        display_mode="standard",
        project_root=base_dir,
    )


def test_about_command(tmp_path):
    context = make_context(tmp_path)
    result = AboutCommand.execute((), context)
    assert result == CommandStatus.HANDLED

    output = context.console.file.getvalue()
    assert "Scyther" in output
    assert "Google DeepMind team" in output
    assert "Apache-2.0" in output
    assert "Repository inspection" in output


def test_version_command(tmp_path):
    context = make_context(tmp_path)
    result = VersionCommand.execute((), context)
    assert result == CommandStatus.HANDLED

    output = context.console.file.getvalue()
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    assert f"Scyther v{__version__}" in output
    assert f"Python {py_ver}" in output


def test_doctor_command(tmp_path):
    context = make_context(tmp_path)
    result = DoctorCommand.execute((), context)
    assert result == CommandStatus.HANDLED

    output = context.console.file.getvalue()
    assert "Active Repository:" in output
    assert str(tmp_path) in output
    assert "Read access: OK" in output
    assert "Write access: OK" in output
    assert "Git Binary:" in output


def test_config_command(tmp_path):
    # Write custom project config
    project_config = tmp_path / ".scyther.toml"
    project_config.write_text("default_tree_depth = 4\nignored_dirs = ['foo']", encoding="utf-8")

    context = make_context(tmp_path)
    result = ConfigCommand.execute((), context)
    assert result == CommandStatus.HANDLED

    output = context.console.file.getvalue()
    assert "Loaded Configs:" in output
    assert "Global:" in output
    assert "Project:" in output
    assert ".scyther.toml (Found)" in output
    assert "Settings:" in output
    assert "default_tree_depth: 4" in output
    assert "foo" in output


def test_help_release_category(tmp_path):
    context = make_context(tmp_path)
    result = CommandRouter.route("/help", context)
    assert result == CommandStatus.HANDLED

    output = context.console.file.getvalue()
    assert "Release Commands" in output
    assert "/about" in output
    assert "/version" in output
    assert "/doctor" in output
    assert "/config" in output


def test_help_specific_release_command(tmp_path):
    context = make_context(tmp_path)
    result = CommandRouter.route("/help config", context)
    assert result == CommandStatus.HANDLED

    output = context.console.file.getvalue()
    assert "Command: /config" in output
    assert "Category:\nRelease" in output
