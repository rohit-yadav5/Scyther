from rich.console import Console

console = Console()


class FileRenderer:
    @staticmethod
    def render_file(file_data):
        console.print(f"File: {file_data['name']}")
        console.print(f"Path: {file_data['path']}")
        console.print()
        console.print(file_data["content"], end="")
        if not file_data["content"].endswith("\n"):
            console.print()

    @staticmethod
    def render_error(message: str):
        console.print(message)
