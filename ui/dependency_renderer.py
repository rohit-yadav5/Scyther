from core.models import FileDependency


class DependencyRenderer:
    @staticmethod
    def render_deps(source_file: str, deps: list[FileDependency], context) -> None:
        context.console.print("Dependencies")
        context.console.print()
        
        context.console.print(source_file)
        
        if not deps:
            context.console.print("  (No dependencies found)")
            return
            
        # Sort targets alphabetically for deterministic tree display
        sorted_deps = sorted(deps, key=lambda d: d.target.lower())
        
        for idx, dep in enumerate(sorted_deps):
            is_last = idx == len(sorted_deps) - 1
            branch = "└─ " if is_last else "├─ "
            context.console.print(f"{branch}{dep.target}")
