from pathlib import Path

from core.config import IGNORED_DIRS
from core.models import MultipleMatchesError
from tools.file_tool import FileTool


class FileService:
    """Project-scoped file access.

    All operations are confined to *root_path*. Files inside ignored
    directories (.git, .venv, __pycache__, etc.) are never returned.
    """

    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        self.file_tool = FileTool

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_ignored(path: Path, root: Path) -> bool:
        """Return True if any relative segment of *path* is in IGNORED_DIRS."""
        try:
            relative = path.relative_to(root)
            return any(part in IGNORED_DIRS for part in relative.parts)
        except ValueError:
            return True  # path escapes root — always ignored

    def _resolve_file(self, filename: str) -> list[Path]:
        """Resolve *filename* to matching absolute paths inside the project root.

        Returns a list:
          - []       → file not found
          - [path]   → exactly one match
          - [a, b…]  → multiple matches (caller must not auto-select)

        Resolution order:
          1. Direct path: ``root / filename`` (supports relative paths like ``src/main.py``).
          2. Recursive glob within the project, skipping ignored directories.
        """
        # 1. Direct path check (handles "src/main.py" style arguments)
        direct = (self.root_path / filename).resolve()
        if (
            direct.is_file()
            and direct.is_relative_to(self.root_path)
            and not self._is_ignored(direct, self.root_path)
        ):
            return [direct]

        # 2. Glob search — collect all matching files in the project
        matches: list[Path] = []
        for path in self.root_path.rglob(filename):
            resolved = path.resolve()
            if (
                resolved.is_file()
                and resolved.is_relative_to(self.root_path)
                and not self._is_ignored(resolved, self.root_path)
            ):
                matches.append(resolved)

        return matches

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def read_file(self, filename: str) -> dict:
        """Read a project file by name or relative path.

        Raises:
            FileNotFoundError:   No matching file found within the project.
            MultipleMatchesError: More than one file matches *filename*.
                                  The caller should display all matches and
                                  ask for a more specific path.
        """
        matches = self._resolve_file(filename)

        if not matches:
            raise FileNotFoundError(f"File not found: {filename}")

        if len(matches) > 1:
            relative_matches = sorted(
                m.relative_to(self.root_path).as_posix() for m in matches
            )
            raise MultipleMatchesError(filename, relative_matches)

        file_path = matches[0]
        contents = self.file_tool.read_file(str(file_path))
        return {
            "path": file_path.relative_to(self.root_path).as_posix(),
            "content": contents,
        }

    def _resolve_mutation_path(self, path_str: str) -> Path:
        """Resolve a path for mutation, enforcing root boundary and IGNORED_DIRS.

        Raises:
            PermissionError: If the target path escapes the project root or
                             falls inside an ignored directory.
        """
        target_path = Path(path_str)
        if not target_path.is_absolute():
            target_path = (self.root_path / target_path).resolve()
        else:
            target_path = target_path.resolve()

        # Enforce project root boundary
        if not target_path.is_relative_to(self.root_path):
            raise PermissionError(f"Access denied: path '{path_str}' is outside project root.")

        # Enforce ignored directories
        try:
            relative = target_path.relative_to(self.root_path)
            if any(part in IGNORED_DIRS for part in relative.parts):
                raise PermissionError(f"Access denied: path '{path_str}' is inside an ignored directory.")
        except ValueError:
            raise PermissionError(f"Access denied: path '{path_str}' is outside project root.")

        return target_path

    def write(self, path: str, content: str) -> str:
        """Writes content to path, enforcing safety boundaries. Included for backwards compatibility."""
        return self.write_file(path, content)

    def create_file(self, filename: str) -> str:
        """Create an empty file, automatically creating parent directories.

        Raises:
            FileExistsError: If the file already exists.
            PermissionError: If the path is outside project root or inside ignored directories.
        """
        resolved_path = self._resolve_mutation_path(filename)
        if resolved_path.exists():
            raise FileExistsError(f"File already exists: {filename}")

        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_tool.write_file(str(resolved_path), "")
        return resolved_path.relative_to(self.root_path).as_posix()

    def create_directory(self, dirname: str) -> str:
        """Create a directory, automatically creating parent directories.

        Raises:
            FileExistsError: If a file or directory already exists at the target path.
            PermissionError: If the path is outside project root or inside ignored directories.
        """
        resolved_path = self._resolve_mutation_path(dirname)
        if resolved_path.exists():
            raise FileExistsError(f"Path already exists: {dirname}")

        resolved_path.mkdir(parents=True, exist_ok=True)
        return resolved_path.relative_to(self.root_path).as_posix()

    def write_file(self, filename: str, content: str) -> str:
        """Write content to a file, automatically creating parent directories.

        Raises:
            IsADirectoryError: If the path is a directory.
            PermissionError: If the path is outside project root or inside ignored directories.
        """
        resolved_path = self._resolve_mutation_path(filename)
        if resolved_path.is_dir():
            raise IsADirectoryError(f"Cannot write to a directory: {filename}")

        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_tool.write_file(str(resolved_path), content)
        return resolved_path.relative_to(self.root_path).as_posix()

    def append_file(self, filename: str, content: str) -> str:
        """Append content to a file, automatically creating parent directories.

        Raises:
            IsADirectoryError: If the path is a directory.
            PermissionError: If the path is outside project root or inside ignored directories.
        """
        resolved_path = self._resolve_mutation_path(filename)
        if resolved_path.is_dir():
            raise IsADirectoryError(f"Cannot append to a directory: {filename}")

        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_tool.append_file(str(resolved_path), content)
        return resolved_path.relative_to(self.root_path).as_posix()

    def replace_text(self, filename: str, old_text: str, new_text: str) -> int:
        """Replace all occurrences of old_text with new_text in an existing file.

        Raises:
            FileNotFoundError: If the file does not exist.
            IsADirectoryError: If the path is a directory.
            PermissionError: If safety boundary check fails.
        """
        resolved_path = self._resolve_mutation_path(filename)
        if not resolved_path.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        if resolved_path.is_dir():
            raise IsADirectoryError(f"Cannot edit a directory: {filename}")

        from tools.edit_tool import EditTool
        return EditTool.replace_text(str(resolved_path), old_text, new_text)

    def delete_path(self, path_str: str, recursive: bool = False) -> None:
        """Delete a file or directory recursively, enforcing safety boundaries.

        Raises:
            FileNotFoundError: If the path does not exist.
            DirectoryDeletionError: If a directory is targeted without recursive=True.
            PermissionError: If safety boundaries fail.
        """
        resolved_path = self._resolve_mutation_path(path_str)
        if not resolved_path.exists():
            raise FileNotFoundError(f"Path not found: {path_str}")

        if resolved_path.is_dir() and not recursive:
            from core.models import DirectoryDeletionError
            raise DirectoryDeletionError(
                f"Directory deletion requires:\n/delete --force {path_str}"
            )

        self.file_tool.delete_path(str(resolved_path), recursive=recursive)

    def move_path(self, source_str: str, destination_str: str) -> str:
        """Move a file or directory, automatically creating parent directories.

        Raises:
            FileNotFoundError: If the source path does not exist.
            PermissionError: If safety boundaries fail.
        """
        src_path = self._resolve_mutation_path(source_str)
        if not src_path.exists():
            raise FileNotFoundError(f"Source not found: {source_str}")

        dest_path = self._resolve_mutation_path(destination_str)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        self.file_tool.move_path(str(src_path), str(dest_path))
        return dest_path.relative_to(self.root_path).as_posix()

    def copy_path(self, source_str: str, destination_str: str) -> str:
        """Copy a file or directory, automatically creating parent directories.

        Raises:
            FileNotFoundError: If the source path does not exist.
            PermissionError: If safety boundaries fail.
        """
        src_path = self._resolve_mutation_path(source_str)
        if not src_path.exists():
            raise FileNotFoundError(f"Source not found: {source_str}")

        dest_path = self._resolve_mutation_path(destination_str)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        self.file_tool.copy_path(str(src_path), str(dest_path), recursive=src_path.is_dir())
        return dest_path.relative_to(self.root_path).as_posix()
