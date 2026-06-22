from pathlib import Path

from scyther.tools.repo_tool import RepoTool


class RepositoryStatsService:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()

    def get_largest_files(self, limit: int = 10) -> list[dict]:
        """Find the largest files in the repository."""
        files_with_size = []
        for root, path in RepoTool._walk(str(self.project_root)):
            if path.is_file():
                try:
                    size = path.stat().st_size
                    rel_path = path.relative_to(root).as_posix()
                    files_with_size.append({"path": rel_path, "size": size})
                except OSError:
                    continue
        
        # Sort descending by size
        files_with_size.sort(key=lambda x: x["size"], reverse=True)
        return files_with_size[:limit]
