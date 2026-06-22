from pathlib import Path
from scyther.tools.git_tool import GitTool


class GitService:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        self.git_tool = GitTool

    def _validate_repository(self) -> None:
        """Validate early that .git directory exists and it is a git repository."""
        dot_git = self.root_path / ".git"
        if not dot_git.exists():
            raise ValueError("Current project is not a git repository.")

        if not self.git_tool.is_git_repository(str(self.root_path)):
            raise ValueError("Current project is not a git repository.")

    def git_status(self) -> str:
        self._validate_repository()
        return self.git_tool.git_status(str(self.root_path))

    def git_diff(self) -> str:
        self._validate_repository()
        return self.git_tool.git_diff(str(self.root_path))
