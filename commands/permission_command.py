from core.config import PERMISSION_MODES
from core.models import CommandStatus
from permissions.permission_manager import PermissionManager
from rich.panel import Panel


class PermissionCommand:
    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        context.console.print("\n===================================")
        context.console.print(" Scyther Permission Mode")
        context.console.print("===================================")
        for key, value in PERMISSION_MODES.items():
            context.console.print(f"{key}. {value}")
        context.console.print("===================================")
        while True:
            choice = input("Select Permission Mode: ").strip()
            if choice in PERMISSION_MODES:
                pm = PermissionManager(context)
                pm.set_permission(choice)
                context.console.print(
                    Panel.fit(PERMISSION_MODES[choice], title="Permission Selected", border_style="green")
                )
                context.console.print()
                break
            context.console.print("Invalid option")
        return CommandStatus.HANDLED
