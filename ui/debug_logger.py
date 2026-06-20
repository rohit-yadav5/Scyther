from datetime import datetime

from rich.console import Console

from core.config import DISPLAY_MODE

console = Console()


def debug_log(message: str):
    if DISPLAY_MODE != "debug":
        return

    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    console.print(f"[{timestamp}] {message}", style="bright_black")
