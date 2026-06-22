from pathlib import Path
from rich.console import Console
from rich.syntax import Syntax

console = Console()

EXTENSION_MAP = {
    ".py": "python",
    ".md": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".sh": "bash",
    ".txt": "text",
    ".ini": "ini",
    ".toml": "toml",
    ".html": "html",
    ".css": "css",
    ".js": "javascript",
    ".ts": "typescript",
}


class FileRenderer:
    @staticmethod
    def render_file(file_data):
        console.print(f"File: {file_data['name']}")
        console.print(f"Path: {file_data['path']}")
        console.print()

        ext = Path(file_data["path"]).suffix.lower()
        lexer = EXTENSION_MAP.get(ext, "text")

        syntax = Syntax(
            file_data["content"],
            lexer,
            theme="monokai",
            line_numbers=True,
        )
        console.print(syntax)

    @staticmethod
    def render_error(message: str):
        console.print(message)
