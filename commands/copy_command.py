from core.models import CommandStatus
from services.file_service import FileService


class CopyCommand:
    """/copy <source> <destination> — copy a file or directory to a new location."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        if len(args) != 2:
            context.console.print("[red]Usage: /copy <source> <destination>[/red]")
            return CommandStatus.HANDLED

        source, destination = args
        service = FileService(str(context.project_root), config=context.config)

        try:
            rel_dest = service.copy_path(source, destination)
            context.console.print(f"[green]Copied: {source} -> {rel_dest}[/green]")
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
