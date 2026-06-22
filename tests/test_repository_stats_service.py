import pytest

from services.repository_stats_service import RepositoryStatsService


def test_get_largest_files(tmp_path):
    # Create files of different sizes
    (tmp_path / "small.txt").write_text("a" * 10)       # 10 bytes
    (tmp_path / "medium.txt").write_text("a" * 100)     # 100 bytes
    (tmp_path / "large.txt").write_text("a" * 1000)     # 1000 bytes

    service = RepositoryStatsService(str(tmp_path))
    
    # Check sorting
    files = service.get_largest_files(limit=10)
    assert len(files) == 3
    assert files[0]["path"] == "large.txt"
    assert files[0]["size"] == 1000
    assert files[1]["path"] == "medium.txt"
    assert files[1]["size"] == 100
    assert files[2]["path"] == "small.txt"
    assert files[2]["size"] == 10

    # Check limit constraint
    files_limited = service.get_largest_files(limit=2)
    assert len(files_limited) == 2
    assert files_limited[0]["path"] == "large.txt"
    assert files_limited[1]["path"] == "medium.txt"
