from pathlib import Path


class SearchService:
    def search(self, root: str, pattern: str):
        matches = []
        for path in Path(root).rglob("*"):
            if path.is_file():
                content = path.read_text(encoding="utf-8", errors="ignore")
                if pattern in content:
                    matches.append(path)
        return matches
