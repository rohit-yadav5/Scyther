from scyther.core.models import CommandStatus
from scyther.services.search_service import SearchService
from scyther.ui.search_renderer import SearchRenderer


class SearchCommand:
    """/search <pattern> — search for a text pattern across all project files."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        if not args:
            context.console.print("[red]Usage: /search <pattern>[/red]")
            return CommandStatus.HANDLED

        pattern = " ".join(args)
        service = SearchService(config=context.config)
        matches = service.search(str(context.project_root), pattern)

        SearchRenderer.render(matches, pattern, context)
        return CommandStatus.HANDLED
