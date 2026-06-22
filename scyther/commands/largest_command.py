from scyther.core.models import CommandStatus
from scyther.services.repository_stats_service import RepositoryStatsService
from scyther.ui.repo_renderer import RepoRenderer


class LargestCommand:
    """/largest [limit] — show largest files in repository."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        limit = 10
        if args:
            try:
                limit = int(args[0])
                if limit <= 0:
                    context.console.print("[red]Limit must be a positive integer.[/red]")
                    return CommandStatus.HANDLED
            except ValueError:
                context.console.print("[red]Usage: /largest \\[limit][/red]")
                return CommandStatus.HANDLED

        service = RepositoryStatsService(str(context.project_root))
        try:
            largest_files = service.get_largest_files(limit)
            RepoRenderer.render_largest(largest_files, context)
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
