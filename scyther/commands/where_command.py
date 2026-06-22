from scyther.core.models import CommandStatus
from scyther.services.code_index_service import CodeIndexService
from scyther.ui.symbol_renderer import SymbolRenderer


class WhereCommand:
    """/where <symbol> — locate symbol definitions."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        if not args:
            context.console.print("[red]Usage: /where <symbol>[/red]")
            return CommandStatus.HANDLED

        symbol = args[0]
        service = CodeIndexService(str(context.project_root), config=context.config)
        try:
            locations = service.find_definitions(symbol)
            SymbolRenderer.render_where(symbol, locations, context)
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
