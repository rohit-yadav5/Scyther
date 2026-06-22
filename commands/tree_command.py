from core.models import CommandStatus
from services.repo_service import RepoService
from ui.repo_renderer import RepoRenderer


class TreeCommand:
    """/tree [depth] — show directory tree with optional depth limit."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        max_depth = None
        if args:
            try:
                max_depth = int(args[0])
            except ValueError:
                context.console.print(
                    f"[red]Invalid depth: '{args[0]}'. Usage: /tree [depth][/red]"
                )
                return CommandStatus.HANDLED

        service = RepoService(str(context.project_root))
        tree = service.show_tree(max_depth=max_depth)
        RepoRenderer.render_tree(tree)
        return CommandStatus.HANDLED
