from core.models import CommandStatus
from services.git_service import GitService


class GitStatusCommand:
    """/git-status — show the Git status of the project root."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        service = GitService(str(context.project_root))

        try:
            status_output = service.git_status()
            if status_output.strip():
                context.console.print(status_output.strip())
            else:
                context.console.print("Working tree clean.")
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
