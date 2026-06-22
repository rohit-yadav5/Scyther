import pytest

from scyther.commands.display_command import DisplayCommand
from scyther.commands.permission_command import PermissionCommand
from scyther.core.models import CommandStatus
from scyther.routing.command_router import CommandRouter


class DummyConsole:
    def print(self, *args, **kwargs):
        pass


class DummyContext:
    def __init__(self, project_root=None):
        self.console = DummyConsole()
        self.current_permission = "3"
        self.display_mode = "standard"
        self._project_root = project_root
        self._config = None

    @property
    def project_root(self):
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        self._project_root = value
        from scyther.services.config_service import ConfigService
        self._config = ConfigService(str(value))

    @property
    def config(self):
        if self._config is None:
            from scyther.services.config_service import ConfigService
            self._config = ConfigService(str(self._project_root or "."))
        return self._config


def test_slash_commands_route_to_expected_status(monkeypatch, tmp_path):
    context = DummyContext()
    context.project_root = tmp_path

    assert CommandRouter.route("/help", context) == CommandStatus.HANDLED
    assert CommandRouter.route("/exit", context) == CommandStatus.EXIT

    # Patch interactive commands to avoid blocking on input()
    monkeypatch.setattr(DisplayCommand, "execute", lambda args, ctx: CommandStatus.HANDLED)
    monkeypatch.setattr(PermissionCommand, "execute", lambda args, ctx: CommandStatus.HANDLED)

    assert CommandRouter.route("/display", context) == CommandStatus.HANDLED
    assert CommandRouter.route("/permission", context) == CommandStatus.HANDLED


def test_new_commands_are_handled(tmp_path):
    context = DummyContext()
    context.project_root = tmp_path

    # Create a minimal file so /open has something to find
    (tmp_path / "test.txt").write_text("hello", encoding="utf-8")

    assert CommandRouter.route("/list", context) == CommandStatus.HANDLED
    assert CommandRouter.route("/tree", context) == CommandStatus.HANDLED
    assert CommandRouter.route("/tree 1", context) == CommandStatus.HANDLED
    assert CommandRouter.route("/open test.txt", context) == CommandStatus.HANDLED
    assert CommandRouter.route("/find test.txt", context) == CommandStatus.HANDLED
    assert CommandRouter.route("/search hello", context) == CommandStatus.HANDLED
    assert CommandRouter.route("/summary", context) == CommandStatus.HANDLED


def test_unknown_command_returns_not_handled():
    context = DummyContext()
    assert CommandRouter.route("/unknown", context) == CommandStatus.NOT_HANDLED
    assert CommandRouter.route("/xyz", context) == CommandStatus.NOT_HANDLED


def test_empty_input_returns_not_handled():
    context = DummyContext()
    assert CommandRouter.route("", context) == CommandStatus.NOT_HANDLED


def test_plain_text_returns_not_handled():
    context = DummyContext()
    # Plain text (no leading slash) is not in the registry — Phase 2: all rejected
    assert CommandRouter.route("show tree", context) == CommandStatus.NOT_HANDLED
    assert CommandRouter.route("list files", context) == CommandStatus.NOT_HANDLED
    assert CommandRouter.route("open README.md", context) == CommandStatus.NOT_HANDLED
