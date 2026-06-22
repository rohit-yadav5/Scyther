from core.models import SymbolLocation


class SymbolRenderer:
    @staticmethod
    def render_where(symbol: str, locations: list[SymbolLocation], context) -> None:
        if not locations:
            context.console.print(f"No definition found for '{symbol}'")
            return

        # Header
        header = "Definition Found" if len(locations) == 1 else "Definitions Found"
        context.console.print(header)
        context.console.print()
        
        for loc in locations:
            context.console.print(loc.symbol)
            context.console.print(f"{loc.path}:{loc.line}")
            context.console.print()

    @staticmethod
    def render_refs(symbol: str, references: list[SymbolLocation], context) -> None:
        if not references:
            context.console.print(f"No references found for '{symbol}'")
            return

        # Header
        context.console.print(f"References ({len(references)})")
        context.console.print()
        
        for ref in references:
            context.console.print(f"{ref.path}:{ref.line}")
