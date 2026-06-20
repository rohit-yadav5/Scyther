from pathlib import Path


class FileTool:
    @staticmethod
    def read_file(path: str):
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not file_path.is_file():
            raise IsADirectoryError(f"Not a file: {path}")
        return file_path.read_text(encoding="utf-8")
