from core.models import CommandStatus
from services.file_service import FileService


class AppendCommand:
    """/append <path> <content> — append content to a file."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        if len(args) < 2:
            context.console.print("[red]Usage: /append <path> <content>[/red]")
            return CommandStatus.HANDLED

        filename = args[0]
        content = " ".join(args[1:])
        service = FileService(str(context.project_root))

        try:
            relative_path = service.append_file(filename, content)
            context.console.print(f"[green]Appended to file: {relative_path}[/green]")
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
