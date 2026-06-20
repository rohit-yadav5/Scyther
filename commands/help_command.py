from rich.panel import Panel

from core.models import CommandStatus


class HelpCommand:
    @staticmethod
    def execute(context):
        context.console.print(
            Panel.fit(
                "/permission   Change permission mode\n/display      Display settings\n/model        Change Ollama model\n/help         Show help\n/exit         Exit Scyther\n/bye          Exit Scyther\n\nBuilt-in Actions\nlist files\nshow files",
                title="Help",
                border_style="blue",
            )
        )
        return CommandStatus.HANDLED
