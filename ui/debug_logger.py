from datetime import datetime

from rich.console import Console

console = Console()


def debug_log(message: str, context):
    if context.display_mode != "debug":
        return

    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    console.print(f"[{timestamp}] {message}", style="bright_black")
