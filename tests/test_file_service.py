import pytest

from scyther.services.file_service import FileService


def test_read_existing_file(tmp_path):
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    service = FileService(str(tmp_path))

    result = service.read_file("README.md")

    assert result == {"path": "README.md", "content": "hello"}


def test_read_missing_file_reports_filename(tmp_path):
    service = FileService(str(tmp_path))

    with pytest.raises(FileNotFoundError, match="File not found: missing.py"):
        service.read_file("missing.py")
