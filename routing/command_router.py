from commands.display_command import DisplayCommand
from commands.help_command import HelpCommand
from commands.model_command import ModelCommand
from commands.permission_command import PermissionCommand
from core.models import CommandStatus


class CommandRouter:
    @staticmethod
    def route(command: str, context):
        if command in ["/exit", "/bye", "exit", "quit"]:
            return CommandStatus.EXIT
        if command == "/help":
            HelpCommand.execute(context)
            return CommandStatus.HANDLED
        if command == "/permission":
            PermissionCommand.execute(context)
            return CommandStatus.HANDLED
        if command == "/display":
            DisplayCommand.execute(context)
            return CommandStatus.HANDLED
        if command == "/model":
            ModelCommand.execute(context)
            return CommandStatus.HANDLED
        return CommandStatus.NOT_HANDLED
