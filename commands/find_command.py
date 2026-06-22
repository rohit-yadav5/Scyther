from core.models import CommandStatus
from services.repo_service import RepoService


class FindCommand:
    """/find <filename> — find a file by name in the repository."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        if not args:
            context.console.print("[red]Usage: /find <filename>[/red]")
            return CommandStatus.HANDLED

        filename = " ".join(args)
        service = RepoService(str(context.project_root), config=context.config)
        matches = service.find_file(filename)

        if matches:
            for match in matches:
                context.console.print(match)
        else:
            context.console.print(f"No files found matching '{filename}'")

        return CommandStatus.HANDLED
