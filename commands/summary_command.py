from core.models import CommandStatus
from services.repo_service import RepoService
from ui.repo_renderer import RepoRenderer


class SummaryCommand:
    """/summary — show repository statistics (file count, directory count)."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        service = RepoService(str(context.project_root), config=context.config)
        summary = service.repo_summary()
        RepoRenderer.render_summary(summary)
        return CommandStatus.HANDLED
