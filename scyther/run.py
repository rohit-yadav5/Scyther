#!/usr/bin/env python3

from pathlib import Path
from rich.console import Console

from scyther.core.config import CURRENT_PERMISSION, DISPLAY_MODE
from scyther.core.models import RuntimeContext
from scyther.ui.terminal import Shell

BASE_DIR = Path(__file__).parent
console = Console()


def main():
    context = RuntimeContext(
        console=console,
        current_permission=CURRENT_PERMISSION,
        display_mode=DISPLAY_MODE,
        project_root=Path.cwd().resolve(),
    )
    shell = Shell(context)
    shell.start()


if __name__ == "__main__":
    main()
