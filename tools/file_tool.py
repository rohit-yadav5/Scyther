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

    @staticmethod
    def write_file(path: str, content: str) -> None:
        file_path = Path(path)
        file_path.write_text(content, encoding="utf-8")

    @staticmethod
    def append_file(path: str, content: str) -> None:
        file_path = Path(path)
        with file_path.open("a", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def delete_path(path: str, recursive: bool = False) -> None:
        file_path = Path(path)
        if file_path.is_file():
            file_path.unlink()
        elif file_path.is_dir():
            if recursive:
                import shutil
                shutil.rmtree(file_path)
            else:
                raise ValueError("Directory deletion requires recursive flag")

    @staticmethod
    def move_path(src: str, dest: str) -> None:
        import shutil
        shutil.move(src, dest)

    @staticmethod
    def copy_path(src: str, dest: str, recursive: bool = False) -> None:
        import shutil
        src_path = Path(src)
        dest_path = Path(dest)
        if src_path.is_dir():
            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dest_path)
