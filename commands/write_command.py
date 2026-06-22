from core.models import CommandStatus
from services.file_service import FileService


class WriteCommand:
    """/write <path> <content> — write content to a file, overwriting existing content."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        if len(args) < 2:
            context.console.print("[red]Usage: /write <path> <content>[/red]")
            return CommandStatus.HANDLED

        filename = args[0]
        content = " ".join(args[1:])
        service = FileService(str(context.project_root))

        try:
            relative_path = service.write_file(filename, content)
            context.console.print(f"[green]Wrote to file: {relative_path}[/green]")
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
