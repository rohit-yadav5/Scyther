from scyther.tools.repo_tool import RepoTool


class RepoService:
    def __init__(self, root_path: str, config=None):
        self.root_path = root_path
        self.config = config
        self.repo_tool = RepoTool

    @property
    def ignored_dirs(self):
        return self.config.ignored_dirs if self.config else None

    def list_files(self):
        files = self.repo_tool.list_files(self.root_path, ignored_dirs=self.ignored_dirs)
        return {
            "root": self.root_path,
            "files": files,
        }

    def show_tree(self, max_depth: int | None = None):
        return self.repo_tool.tree(self.root_path, max_depth=max_depth, ignored_dirs=self.ignored_dirs)

    def find_file(self, filename: str):
        return self.repo_tool.find_file(self.root_path, filename, ignored_dirs=self.ignored_dirs)

    def repo_summary(self):
        return self.repo_tool.count_files(self.root_path, ignored_dirs=self.ignored_dirs)

    def get_stats(self):
        return self.repo_tool.stats(self.root_path, ignored_dirs=self.ignored_dirs)

    def get_recent_files(self, limit: int = 20) -> list[dict]:
        return self.repo_tool.recent_files(self.root_path, limit, ignored_dirs=self.ignored_dirs)
