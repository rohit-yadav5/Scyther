from pathlib import Path


class EditTool:
    @staticmethod
    def replace_text(path: str, old_text: str, new_text: str) -> int:
        """Replace all occurrences of old_text with new_text in the file at path.

        Returns:
            The number of replacements made.
        """
        file_path = Path(path)
        content = file_path.read_text(encoding="utf-8")
        count = content.count(old_text)
        if count == 0:
            return 0
        new_content = content.replace(old_text, new_text)
        file_path.write_text(new_content, encoding="utf-8")
        return count
