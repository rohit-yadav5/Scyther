from core.models import CommandStatus


class AboutCommand:
    """/about — display general information about Scyther."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        context.console.print("[bold cyan]Scyther[/bold cyan]: A command-first CLI utility for developers.")
        context.console.print("Developed by: Google DeepMind team")
        context.console.print("License: Apache-2.0")
        context.console.print("Core capabilities: Repository inspection, navigation, safe file mutations, developer helper utilities.")
        return CommandStatus.HANDLED
