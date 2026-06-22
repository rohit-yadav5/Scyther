from scyther.core.models import CommandStatus
from scyther.services.repo_service import RepoService


class StatsCommand:
    """/stats — display project statistics."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        service = RepoService(str(context.project_root), config=context.config)

        try:
            stats = service.get_stats()
            context.console.print("Project Statistics")
            context.console.print(f"Files: {stats['files']}")
            context.console.print(f"Directories: {stats['directories']}")
            context.console.print(f"Python Files: {stats['python']}")
            context.console.print(f"Markdown Files: {stats['markdown']}")
            context.console.print(f"JSON Files: {stats['json']}")
            context.console.print(f"Largest File: {stats['largest_file']}")
            context.console.print(f"Largest File Size: {stats['largest_size_kb']} KB")
            context.console.print(f"Total Project Size: {stats['total_size_kb']} KB")
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
