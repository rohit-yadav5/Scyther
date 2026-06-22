from pathlib import Path

from core.config import IGNORED_DIRS


class RepoTool:
    @classmethod
    def _should_ignore(cls, path: Path, root: Path, ignored_dirs=None) -> bool:
        """Return True if any relative segment of *path* is in ignored directories."""
        if ignored_dirs is None:
            ignored_dirs = IGNORED_DIRS
        try:
            relative = path.relative_to(root)
            return any(part in ignored_dirs for part in relative.parts)
        except ValueError:
            return True  # path escapes root — always ignore

    @classmethod
    def _walk(cls, root_path: str, ignored_dirs=None):
        root = Path(root_path).resolve()
        for path in root.rglob("*"):
            if cls._should_ignore(path, root, ignored_dirs):
                continue
            yield root, path

    @classmethod
    def list_files(cls, root_path: str, ignored_dirs=None):
        files = []
        for _, path in cls._walk(root_path, ignored_dirs):
            if path.is_file():
                files.append(path.relative_to(Path(root_path).resolve()).as_posix())
        return sorted(files)

    @classmethod
    def tree(cls, root_path: str, max_depth: int | None = None, ignored_dirs=None):
        root = Path(root_path).resolve()
        directories: set[str] = set()
        files: list[str] = []

        def build_node(path: Path, depth: int) -> dict:
            children: list[dict] = []
            if max_depth is not None and depth >= max_depth:
                return {"name": path.name or ".", "type": "directory", "path": "", "children": children}

            visible_children = [
                child
                for child in sorted(path.iterdir(), key=lambda item: (item.is_file(), item.name.lower()))
                if not cls._should_ignore(child, root, ignored_dirs)
            ]

            for child in visible_children:
                relative = child.relative_to(root).as_posix()
                if child.is_dir():
                    directories.add(relative)
                    children.append(build_node(child, depth + 1))
                elif child.is_file():
                    files.append(relative)
                    children.append(
                        {
                            "name": child.name,
                            "type": "file",
                            "path": relative,
                            "children": [],
                        }
                    )

            return {
                "name": root.name if path == root else path.name,
                "type": "directory",
                "path": "" if path == root else path.relative_to(root).as_posix(),
                "children": children,
            }

        # build_node populates `directories` and `files` as a side effect.
        # It must be called before the return dict is constructed so that
        # sorted(directories) and sorted(files) reflect the full traversal.
        tree_node = build_node(root, 0)

        return {
            "root": root.as_posix(),
            "directories": sorted(directories),
            "files": sorted(files),
            "tree": tree_node,
            "max_depth": max_depth,
        }

    @classmethod
    def find_file(cls, root_path: str, filename: str, ignored_dirs=None):
        matches = []
        for _, path in cls._walk(root_path, ignored_dirs):
            if path.is_file() and path.name == filename:
                matches.append(path.relative_to(Path(root_path).resolve()).as_posix())
        return sorted(matches)

    @classmethod
    def count_files(cls, root_path: str, ignored_dirs=None):
        root = Path(root_path).resolve()
        file_count = 0
        directories: set[str] = set()

        for _, path in cls._walk(root_path, ignored_dirs):
            relative = path.relative_to(root)
            if path.is_file():
                file_count += 1
                parent = relative.parent
                while parent != Path("."):
                    directories.add(parent.as_posix())
                    parent = parent.parent
            elif path.is_dir():
                directories.add(relative.as_posix())

        return {
            "root": root.as_posix(),
            "files": file_count,
            "directories": len(directories),
        }

    @classmethod
    def stats(cls, root_path: str, ignored_dirs=None):
        root = Path(root_path).resolve()
        file_count = 0
        directories: set[str] = set()
        py_count = 0
        md_count = 0
        json_count = 0

        largest_file_path = None
        largest_file_size = 0
        total_size = 0

        for _, path in cls._walk(root_path, ignored_dirs):
            relative = path.relative_to(root)
            if path.is_file():
                file_count += 1
                parent = relative.parent
                while parent != Path("."):
                    directories.add(parent.as_posix())
                    parent = parent.parent

                try:
                    size = path.stat().st_size
                except OSError:
                    size = 0
                total_size += size
                if size > largest_file_size:
                    largest_file_size = size
                    largest_file_path = path

                suffix = path.suffix.lower()
                if suffix == ".py":
                    py_count += 1
                elif suffix == ".md":
                    md_count += 1
                elif suffix == ".json":
                    json_count += 1
            elif path.is_dir():
                directories.add(relative.as_posix())

        largest_size_kb = round(largest_file_size / 1024)
        total_size_kb = round(total_size / 1024)
        largest_file_name = largest_file_path.name if largest_file_path else "None"

        return {
            "files": file_count,
            "directories": len(directories),
            "python": py_count,
            "markdown": md_count,
            "json": json_count,
            "largest_file": largest_file_name,
            "largest_size_kb": largest_size_kb,
            "total_size_kb": total_size_kb,
        }

    @classmethod
    def recent_files(cls, root_path: str, limit: int = 20, ignored_dirs=None) -> list[dict]:
        root = Path(root_path).resolve()
        files_with_mtime = []

        for _, path in cls._walk(root_path, ignored_dirs):
            if path.is_file():
                try:
                    mtime = path.stat().st_mtime
                except OSError:
                    continue
                files_with_mtime.append((path, mtime))

        files_with_mtime.sort(key=lambda x: x[1], reverse=True)

        results = []
        for path, mtime in files_with_mtime[:limit]:
            from datetime import datetime
            timestamp = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            results.append({
                "path": path.relative_to(root).as_posix(),
                "timestamp": timestamp
            })

        return results
