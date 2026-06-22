from scyther.tools.repo_tool import RepoTool


def build_repo(root):
    (root / "commands").mkdir()
    (root / "commands" / "help.py").write_text("help", encoding="utf-8")
    (root / "commands" / "nested").mkdir()
    (root / "commands" / "nested" / "deep.py").write_text("deep", encoding="utf-8")
    (root / ".git").mkdir()
    (root / ".git" / "ignored.py").write_text("ignored", encoding="utf-8")
    (root / "__pycache__").mkdir()
    (root / "__pycache__" / "ignored.pyc").write_text("ignored", encoding="utf-8")
    (root / "README.md").write_text("readme", encoding="utf-8")


def test_list_files_ignores_internal_directories(tmp_path):
    build_repo(tmp_path)

    assert RepoTool.list_files(str(tmp_path)) == [
        "README.md",
        "commands/help.py",
        "commands/nested/deep.py",
    ]


def test_tree_is_recursive(tmp_path):
    build_repo(tmp_path)

    tree = RepoTool.tree(str(tmp_path))

    assert "commands/nested" in tree["directories"]
    assert "commands/nested/deep.py" in tree["files"]


def test_tree_depth_limits_children(tmp_path):
    build_repo(tmp_path)

    tree_2 = RepoTool.tree(str(tmp_path), max_depth=2)
    tree_4 = RepoTool.tree(str(tmp_path), max_depth=4)

    assert "commands/nested/deep.py" not in tree_2["files"]
    assert "commands/nested/deep.py" in tree_4["files"]
    assert tree_2 != tree_4


def test_repo_summary_counts_visible_files_and_directories(tmp_path):
    build_repo(tmp_path)

    summary = RepoTool.count_files(str(tmp_path))

    assert summary["files"] == 3
    assert summary["directories"] == 2
