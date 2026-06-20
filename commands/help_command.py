from rich.panel import Panel

from core.models import CommandStatus


class HelpCommand:
    @staticmethod
    def execute(context):
        context.console.print(
            Panel.fit(
                "/permission   Change permission mode\n/display      Display settings\n/help         Show help\n/exit         Exit Scyther",
                title="Help",
                border_style="blue",
            )
        )
        return CommandStatus.HANDLED
