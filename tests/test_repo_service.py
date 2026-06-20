from services.repo_service import RepoService


def test_repo_service_list_files(tmp_path):
    (tmp_path / "README.md").write_text("readme", encoding="utf-8")
    service = RepoService(str(tmp_path))

    assert service.list_files()["files"] == ["README.md"]


def test_repo_service_tree_depth(tmp_path):
    (tmp_path / "a" / "b").mkdir(parents=True)
    (tmp_path / "a" / "b" / "c.py").write_text("c", encoding="utf-8")
    service = RepoService(str(tmp_path))

    tree_2 = service.show_tree(max_depth=2)
    tree_4 = service.show_tree(max_depth=4)

    assert "a/b/c.py" not in tree_2["files"]
    assert "a/b/c.py" in tree_4["files"]


def test_repo_service_summary(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "file.py").write_text("file", encoding="utf-8")
    service = RepoService(str(tmp_path))

    summary = service.repo_summary()

    assert summary["files"] == 1
    assert summary["directories"] == 1
