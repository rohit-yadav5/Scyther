from commands.display_command import DisplayCommand
from commands.permission_command import PermissionCommand
from core.models import CommandStatus
from routing.command_router import CommandRouter


class DummyConsole:
    def print(self, *args, **kwargs):
        pass


class DummyContext:
    console = DummyConsole()
    current_permission = "3"
    display_mode = "standard"


def test_slash_commands_route_to_expected_status(monkeypatch):
    context = DummyContext()

    assert CommandRouter.route("/help", context) == CommandStatus.HANDLED
    assert CommandRouter.route("/exit", context) == CommandStatus.EXIT

    monkeypatch.setattr(DisplayCommand, "execute", lambda ctx: CommandStatus.HANDLED)
    monkeypatch.setattr(PermissionCommand, "execute", lambda ctx: CommandStatus.HANDLED)

    assert CommandRouter.route("/display", context) == CommandStatus.HANDLED
    assert CommandRouter.route("/permission", context) == CommandStatus.HANDLED
