from core.models import CommandStatus
from services.file_service import FileService


class ReplaceCommand:
    """/replace <path> <old_text> <new_text> — replace occurrences of old_text with new_text inside file."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        if len(args) != 3:
            context.console.print("[red]Usage: /replace <path> <old_text> <new_text>[/red]")
            return CommandStatus.HANDLED

        filename, old_text, new_text = args
        service = FileService(str(context.project_root), config=context.config)

        try:
            count = service.replace_text(filename, old_text, new_text)
            if count > 0:
                context.console.print(f"Replaced {count} occurrence(s)")
            else:
                context.console.print("No matches found")
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
