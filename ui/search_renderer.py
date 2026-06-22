import re
from rich.markup import escape


class SearchRenderer:
    @staticmethod
    def render(results: list[dict], pattern: str, context) -> None:
        total = len(results)
        context.console.print(f"Found {total} matches")

        if total == 0:
            return

        context.console.print()  # Blank line after header

        limit = 50
        display_results = results[:limit]

        if total > limit:
            context.console.print(f"Showing first {limit} matches.")
            context.console.print()

        for i, match in enumerate(display_results):
            # Print file path and line number in the standard path:line_number format
            path_line = f"{match['path']}:{match['line_number']}"
            context.console.print(path_line)

            # Highlight matched term case-insensitively in the line
            line = match["line"]
            escaped_line = escape(line)
            escaped_pattern = escape(pattern)

            # Use case-insensitive regex substitution to wrap the matched string in highlighting tags
            highlighted_line = re.sub(
                re.escape(escaped_pattern),
                lambda m: f"[bold yellow]{m.group(0)}[/bold yellow]",
                escaped_line,
                flags=re.IGNORECASE
            )
            context.console.print(highlighted_line)

            # Blank line between matches
            if i < len(display_results) - 1:
                context.console.print()
