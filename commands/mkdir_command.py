from core.models import CommandStatus
from services.file_service import FileService


class MkdirCommand:
    """/mkdir <path> — create a directory, automatically creating parent directories."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        if not args:
            context.console.print("[red]Usage: /mkdir <path>[/red]")
            return CommandStatus.HANDLED

        dirname = " ".join(args)
        service = FileService(str(context.project_root))

        try:
            relative_path = service.create_directory(dirname)
            context.console.print(f"[green]Created directory: {relative_path}[/green]")
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
