from scyther.core.models import CommandStatus


class ExitCommand:
    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        return CommandStatus.EXIT
