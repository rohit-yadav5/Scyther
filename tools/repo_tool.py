from pathlib import Path


class RepoTool:
    IGNORED_DIRS = {".git", ".venv", "node_modules", "dist", "build", "__pycache__", "pycache"}

    @classmethod
    def _should_ignore(cls, path: Path) -> bool:
        return any(part in cls.IGNORED_DIRS for part in path.parts)

    @classmethod
    def _walk(cls, root_path: str):
        root = Path(root_path).resolve()
        for path in root.rglob("*"):
            if cls._should_ignore(path):
                continue
            yield root, path

    @classmethod
    def list_files(cls, root_path: str):
        files = []
        for _, path in cls._walk(root_path):
            if path.is_file():
                files.append(path.relative_to(Path(root_path).resolve()).as_posix())
        return sorted(files)

    @classmethod
    def tree(cls, root_path: str, max_depth: int | None = None):
        root = Path(root_path).resolve()
        directories = set()
        files = []

        def build_node(path: Path, depth: int):
            children = []
            if max_depth is not None and depth >= max_depth:
                return {"name": path.name or ".", "type": "directory", "path": "", "children": children}

            visible_children = [
                child
                for child in sorted(path.iterdir(), key=lambda item: (item.is_file(), item.name.lower()))
                if not cls._should_ignore(child)
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

        return {
            "root": root.as_posix(),
            "directories": sorted(directories),
            "files": sorted(files),
            "tree": build_node(root, 0),
            "max_depth": max_depth,
        }

    @classmethod
    def find_file(cls, root_path: str, filename: str):
        matches = []
        for _, path in cls._walk(root_path):
            if path.is_file() and path.name == filename:
                matches.append(path.relative_to(Path(root_path).resolve()).as_posix())
        return sorted(matches)

    @classmethod
    def count_files(cls, root_path: str):
        root = Path(root_path).resolve()
        file_count = 0
        directories = set()

        for _, path in cls._walk(root_path):
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
