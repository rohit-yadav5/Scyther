from core.models import CommandStatus
from services.file_service import FileService


class CreateCommand:
    """/create <path> — create an empty file, automatically creating parent directories."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        if not args:
            context.console.print("[red]Usage: /create <path>[/red]")
            return CommandStatus.HANDLED

        filename = " ".join(args)
        service = FileService(str(context.project_root))

        try:
            relative_path = service.create_file(filename)
            context.console.print(f"[green]Created empty file: {relative_path}[/green]")
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
