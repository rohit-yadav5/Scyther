import os
from pathlib import Path

from core.errors import PermissionDeniedError


class PathService:
    def __init__(self, project_root: str, ignored_dirs: frozenset[str] = frozenset()):
        self.project_root = Path(project_root).resolve()
        self.ignored_dirs = ignored_dirs

    def normalize(self, path_str: str) -> Path:
        """Expand user home (~), normalize path, and resolve to absolute Path."""
        p = Path(os.path.expanduser(path_str))
        if not p.is_absolute():
            p = (self.project_root / p).resolve()
        else:
            p = p.resolve()
        return p

    def is_within_root(self, path: Path) -> bool:
        """Check if absolute path is inside the project root."""
        try:
            return path.is_relative_to(self.project_root)
        except ValueError:
            return False

    def is_ignored(self, path: Path) -> bool:
        """Check if any path segment relative to project root matches ignored_dirs."""
        if not self.is_within_root(path):
            return True
        try:
            relative = path.relative_to(self.project_root)
            return any(part in self.ignored_dirs for part in relative.parts)
        except ValueError:
            return True

    def resolve_and_validate(self, path_str: str, check_ignored: bool = True) -> Path:
        """Resolve path and validate boundaries and ignored directories constraints."""
        resolved = self.normalize(path_str)
        if not self.is_within_root(resolved):
            raise PermissionDeniedError(f"Access denied: path '{path_str}' is outside project root.")
        if check_ignored and self.is_ignored(resolved):
            raise PermissionDeniedError(f"Access denied: path '{path_str}' is inside an ignored directory.")
        return resolved
