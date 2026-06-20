from core.models import IntentCategories
from routing.intent_router import IntentRouter


def test_tree_phrases_route_to_repo_tree():
    samples = [
        "show tree",
        "show the tree",
        "full tree",
        "show full tree",
        "show a full tree",
        "tree 2",
        "tree 4",
        "repository tree",
        "repository structure",
        "project structure",
        "show file structure",
    ]

    for sample in samples:
        assert IntentRouter.route(sample) == IntentCategories.REPO_TREE


def test_file_read_phrases_route_to_file_read():
    samples = ["open README.md", "read README.md", "show file README.md"]

    for sample in samples:
        result = IntentRouter.inspect(sample)
        assert result.intent == IntentCategories.FILE_READ
        assert result.extracted_entities["filenames"] == ["README.md"]


def test_list_files_routes_to_repo_list():
    assert IntentRouter.route("list files") == IntentCategories.REPO_LIST


def test_tree_depth_entity_is_extracted():
    result = IntentRouter.inspect("tree 4")

    assert result.intent == IntentCategories.REPO_TREE
    assert result.extracted_entities["depth"] == 4
