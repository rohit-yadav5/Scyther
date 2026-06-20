from rich.console import Console
from rich.panel import Panel

from core.config import DISPLAY_MODE

console = Console()


def show_display_settings():
    console.print(
        Panel.fit(
            "1. Minimal\n2. Standard (Recommended)\n3. Verbose\n4. Debug",
            title="Display Mode",
            border_style="cyan",
        )
    )


def show_active_display(display_mode=DISPLAY_MODE):
    console.print(
        Panel.fit(
            f"Active Mode: {display_mode.upper()}",
            title="Display Updated",
            border_style="green",
        )
    )
