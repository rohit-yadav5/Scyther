from core.models import CommandStatus
from services.repo_service import RepoService


class RecentCommand:
    """/recent [limit] — show recently modified project files."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        limit = 20
        if args:
            try:
                limit = int(args[0])
            except ValueError:
                context.console.print("[red]Usage: /recent [limit][/red]")
                return CommandStatus.HANDLED

        service = RepoService(str(context.project_root))

        try:
            recent_files = service.get_recent_files(limit)
            if not recent_files:
                context.console.print("No files found.")
                return CommandStatus.HANDLED

            for file_info in recent_files:
                context.console.print(file_info["path"])
                context.console.print(f"  {file_info['timestamp']}")
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
