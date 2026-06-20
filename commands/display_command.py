from ui.display_manager import show_active_display, show_display_settings
from core.models import CommandStatus


class DisplayCommand:
    @staticmethod
    def execute(context):
        show_display_settings()
        choice = input("display> ").strip()
        mapping = {"1": "minimal", "2": "standard", "3": "verbose", "4": "debug"}
        if choice in mapping:
            context.display_mode = mapping[choice]
            show_active_display(context.display_mode)
        return CommandStatus.HANDLED
