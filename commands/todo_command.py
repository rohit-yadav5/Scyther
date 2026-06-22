import re
from rich.markup import escape

from core.models import CommandStatus
from services.search_service import SearchService


class TodoCommand:
    """/todo — scan project for TODO/FIXME/HACK/BUG tags."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        service = SearchService()

        try:
            results = service.todo(str(context.project_root))
            context.console.print(f"Found {len(results)} matches")
            if not results:
                return CommandStatus.HANDLED

            context.console.print()

            keywords = ["TODO", "FIXME", "HACK", "BUG"]
            pattern_re = "|".join(re.escape(kw) for kw in keywords)

            for i, match in enumerate(results):
                path_line = f"{match['path']}:{match['line_number']}"
                context.console.print(path_line)

                line = match["line"]
                escaped_line = escape(line)

                highlighted_line = re.sub(
                    pattern_re,
                    lambda m: f"[bold yellow]{m.group(0)}[/bold yellow]",
                    escaped_line,
                    flags=re.IGNORECASE
                )
                context.console.print(highlighted_line)

                if i < len(results) - 1:
                    context.console.print()
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
