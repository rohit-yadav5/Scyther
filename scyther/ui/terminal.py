from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from scyther.core.models import CommandStatus, RuntimeContext
from scyther.routing.command_router import CommandRouter

console = Console()


class Shell:
    def __init__(self, context: RuntimeContext):
        self.context = context

    def start(self) -> None:
        from scyther.core.version import __version__
        from scyther.core.command_registry import COMMANDS
        from scyther.permissions.access_control import AccessControl

        permission_behavior = AccessControl.get_behavior(self.context.current_permission)
        display_mode_str = self.context.display_mode.capitalize()
        total_commands = len(COMMANDS)

        self.context.console.print(
            Panel.fit(
                f"Project: {self.context.project_root}"
                f"\nPermission: {permission_behavior}"
                f"\nDisplay: {display_mode_str}"
                f"\nCommands: {total_commands}",
                title=f"Scyther v{__version__}",
                border_style="cyan",
            )
        )
        self.context.console.print()

        while True:
            prompt = input("scyther> ").strip()
            if not prompt:
                continue

            command_result = CommandRouter.route(prompt, self.context)
            if command_result == CommandStatus.EXIT:
                self.context.console.print("Goodbye")
                break
            if command_result == CommandStatus.HANDLED:
                continue

            # All unrecognized input is rejected.
            # Commands must start with "/" — use /help to see available commands.
            self.context.console.print(
                "Unknown command. Type [bold]/help[/bold] for available commands."
            )
