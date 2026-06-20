import pytest

from tools.file_tool import FileTool


def test_read_existing_file(tmp_path):
    file_path = tmp_path / "README.md"
    file_path.write_text("hello", encoding="utf-8")

    assert FileTool.read_file(str(file_path)) == "hello"


def test_read_missing_file_raises_meaningful_error(tmp_path):
    missing = tmp_path / "missing.py"

    with pytest.raises(FileNotFoundError, match="File not found"):
        FileTool.read_file(str(missing))
