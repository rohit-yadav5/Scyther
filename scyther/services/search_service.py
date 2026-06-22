from pathlib import Path

from scyther.core.config import IGNORED_DIRS


class SearchService:
    def __init__(self, config=None):
        self.config = config
        self.ignored_dirs = config.ignored_dirs if config else IGNORED_DIRS
    """Project-scoped content search.

    Searches for a literal string pattern in all readable files within
    the project root, respecting IGNORED_DIRS.

    Returns a list of match dicts with keys:
        path        — relative path from project root
        line_number — 1-indexed line number of the match
        line        — the full matching line (stripped)

    This interface is designed for the future /search command (Phase 4).
    """

    def search(self, root: str, pattern: str) -> list[dict]:
        root_path = Path(root).resolve()
        matches: list[dict] = []

        for path in root_path.rglob("*"):
            if not path.is_file():
                continue

            # Enforce project root and ignore hidden/cache dirs
            try:
                relative = path.relative_to(root_path)
            except ValueError:
                continue
            if any(part in self.ignored_dirs for part in relative.parts):
                continue

            # Read and scan line by line
            try:
                lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue

            pattern_lower = pattern.lower()
            for line_number, line in enumerate(lines, start=1):
                if pattern_lower in line.lower():
                    matches.append(
                        {
                            "path": relative.as_posix(),
                            "line_number": line_number,
                            "line": line.strip(),
                        }
                    )

        return matches

    def todo(self, root: str) -> list[dict]:
        root_path = Path(root).resolve()
        matches: list[dict] = []
        keywords = ["todo", "fixme", "hack", "bug"]

        for path in root_path.rglob("*"):
            if not path.is_file():
                continue

            try:
                relative = path.relative_to(root_path)
            except ValueError:
                continue
            if any(part in self.ignored_dirs for part in relative.parts):
                continue

            try:
                lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue

            for line_number, line in enumerate(lines, start=1):
                line_lower = line.lower()
                if any(kw in line_lower for kw in keywords):
                    matches.append(
                        {
                            "path": relative.as_posix(),
                            "line_number": line_number,
                            "line": line.strip(),
                        }
                    )

        return matches
