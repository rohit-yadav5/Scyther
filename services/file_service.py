from pathlib import Path

from tools.file_tool import FileTool


class FileService:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        self.file_tool = FileTool

    def _resolve_file(self, filename: str):
        direct_path = (self.root_path / filename).resolve()
        if direct_path.exists() and direct_path.is_file():
            return direct_path

        for path in self.root_path.rglob(filename):
            if path.is_file():
                return path.resolve()

        raise FileNotFoundError(f"File not found: {filename}")

    def read_file(self, filename: str):
        file_path = self._resolve_file(filename)
        contents = self.file_tool.read_file(str(file_path))
        return {
            "path": file_path.relative_to(self.root_path).as_posix(),
            "content": contents,
        }

    def write(self, path: str, content: str):
        file_path = Path(path)
        file_path.write_text(content, encoding="utf-8")
        return path
