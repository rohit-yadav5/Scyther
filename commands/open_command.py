from pathlib import Path

from core.models import CommandStatus, MultipleMatchesError
from services.file_service import FileService
from ui.file_renderer import FileRenderer


class OpenCommand:
    """/open <filename> — open and display a file."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        if not args:
            context.console.print("[red]Usage: /open <filename>[/red]")
            return CommandStatus.HANDLED

        # Join args to support filenames with spaces, e.g. /open my notes.txt
        filename = " ".join(args)
        service = FileService(str(context.project_root))

        try:
            result = service.read_file(filename)
        except MultipleMatchesError as exc:
            context.console.print(f"\nMultiple matches found for [bold]{exc.filename}[/bold]:")
            for match in exc.matches:
                context.console.print(f"  {match}")
            context.console.print("\nUse the full path to open a specific file:")
            context.console.print(f"  /open {exc.matches[0]}")
            return CommandStatus.HANDLED
        except FileNotFoundError as exc:
            FileRenderer.render_error(str(exc))
            return CommandStatus.HANDLED
        except IsADirectoryError as exc:
            FileRenderer.render_error(str(exc))
            return CommandStatus.HANDLED

        FileRenderer.render_file(
            {
                "name": Path(result["path"]).name,
                "path": result["path"],
                "content": result["content"],
            }
        )
        return CommandStatus.HANDLED
