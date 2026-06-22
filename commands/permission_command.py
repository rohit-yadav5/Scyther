from core.config import PERMISSION_MODES
from core.models import CommandStatus
from permissions.permission_manager import PermissionManager
from rich.panel import Panel


class PermissionCommand:
    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        print("\n===================================")
        print(" Scyther Permission Mode")
        print("===================================")
        for key, value in PERMISSION_MODES.items():
            print(f"{key}. {value}")
        print("===================================")
        while True:
            choice = input("Select Permission Mode: ").strip()
            if choice in PERMISSION_MODES:
                pm = PermissionManager(context)
                pm.set_permission(choice)
                context.console.print(
                    Panel.fit(PERMISSION_MODES[choice], title="Permission Selected", border_style="green")
                )
                print()
                break
            print("Invalid option")
        return CommandStatus.HANDLED
