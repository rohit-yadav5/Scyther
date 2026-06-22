from core.models import CommandStatus
from services.code_index_service import CodeIndexService
from ui.symbol_renderer import SymbolRenderer


class RefsCommand:
    """/refs <symbol> — locate symbol references/usages."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        if not args:
            context.console.print("[red]Usage: /refs <symbol>[/red]")
            return CommandStatus.HANDLED

        symbol = args[0]
        service = CodeIndexService(str(context.project_root), config=context.config)
        try:
            references = service.find_references(symbol)
            SymbolRenderer.render_refs(symbol, references, context)
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
