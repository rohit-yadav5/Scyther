from scyther.core.models import CommandStatus
from scyther.services.repo_service import RepoService
from scyther.ui.repo_renderer import RepoRenderer


class ListCommand:
    """/list — list all files in the repository."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        service = RepoService(str(context.project_root), config=context.config)
        result = service.list_files()
        RepoRenderer.render_file_list(result["files"])
        return CommandStatus.HANDLED
