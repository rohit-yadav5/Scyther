from pathlib import Path

from scyther.core.models import CommandStatus
from scyther.services.code_index_service import CodeIndexService
from scyther.ui.dependency_renderer import DependencyRenderer


class DepsCommand:
    """/deps <path> — show direct internal dependencies for a file."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        if not args:
            context.console.print("[red]Usage: /deps <path>[/red]")
            return CommandStatus.HANDLED

        file_path_str = " ".join(args)
        service = CodeIndexService(str(context.project_root), config=context.config)
        try:
            dependencies = service.get_dependencies(file_path_str)
            
            from scyther.services.file_service import FileService
            file_service = FileService(str(context.project_root), config=context.config)
            try:
                resolved_abs = file_service.resolve_path(file_path_str)
                source_rel = Path(resolved_abs).relative_to(context.project_root).as_posix()
            except Exception:
                source_rel = file_path_str
                
            DependencyRenderer.render_deps(source_rel, dependencies, context)
        except FileNotFoundError as exc:
            context.console.print(f"[red]Error: {exc}[/red]")
        except Exception as exc:
            context.console.print(f"[red]Error: {exc}[/red]")

        return CommandStatus.HANDLED
