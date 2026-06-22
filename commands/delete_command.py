from core.models import CommandStatus, DirectoryDeletionError
from services.file_service import FileService


class DeleteCommand:
    """/delete [--force] <path> — delete a file, or recursively delete a directory using --force."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        recursive = False
        target_args = args
        if args and args[0] == "--force":
            recursive = True
            target_args = args[1:]

        if not target_args:
            context.console.print("[red]Usage: /delete [--force] <path>[/red]")
            return CommandStatus.HANDLED

        path_str = " ".join(target_args)
        service = FileService(str(context.project_root))

        try:
            service.delete_path(path_str, recursive=recursive)
            context.console.print(f"[green]Deleted: {path_str}[/green]")
        except DirectoryDeletionError as exc:
            context.console.print(str(exc))
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
