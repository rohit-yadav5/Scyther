from scyther.core.models import CommandStatus
from scyther.services.git_service import GitService


class GitDiffCommand:
    """/git-diff — show the Git working tree diff."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        service = GitService(str(context.project_root))

        try:
            diff_output = service.git_diff()
            if not diff_output.strip():
                context.console.print("No changes in working tree.")
                return CommandStatus.HANDLED

            lines = diff_output.splitlines()
            limit = 500
            if len(lines) > limit:
                truncated_diff = "\n".join(lines[:limit])
                context.console.print(truncated_diff)
                context.console.print()
                context.console.print(
                    f"[yellow]Warning: Diff output truncated to first {limit} lines.[/yellow]"
                )
            else:
                context.console.print(diff_output.strip())
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
