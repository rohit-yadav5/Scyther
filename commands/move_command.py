from core.models import CommandStatus
from services.file_service import FileService


class MoveCommand:
    """/move <source> <destination> — move a file or directory to a new location."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        if len(args) != 2:
            context.console.print("[red]Usage: /move <source> <destination>[/red]")
            return CommandStatus.HANDLED

        source, destination = args
        service = FileService(str(context.project_root))

        try:
            rel_dest = service.move_path(source, destination)
            context.console.print(f"[green]Moved: {source} -> {rel_dest}[/green]")
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
