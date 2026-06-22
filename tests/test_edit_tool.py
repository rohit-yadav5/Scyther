import pytest
from pathlib import Path
from tools.edit_tool import EditTool


def test_replace_text_success(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello world", encoding="utf-8")

    count = EditTool.replace_text(str(file_path), "world", "everyone")
    assert count == 1
    assert file_path.read_text(encoding="utf-8") == "hello everyone"


def test_replace_text_multiple_occurrences(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("apple banana apple cherry apple", encoding="utf-8")

    count = EditTool.replace_text(str(file_path), "apple", "orange")
    assert count == 3
    assert file_path.read_text(encoding="utf-8") == "orange banana orange cherry orange"


def test_replace_text_no_matches(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello world", encoding="utf-8")

    count = EditTool.replace_text(str(file_path), "missing", "found")
    assert count == 0
    assert file_path.read_text(encoding="utf-8") == "hello world"


def test_replace_text_file_not_found():
    with pytest.raises(FileNotFoundError):
        EditTool.replace_text("/nonexistent/file.txt", "old", "new")
