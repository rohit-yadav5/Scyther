from core.models import IntentCategories
from routing.intent_engine.models import IntentRule


INTENT_RULES = [
    IntentRule(
        IntentCategories.REPO_LIST,
        ("list", "files", "repository"),
        ("show files", "display repository files", "what files exist", "list all project files", "show me the files", "list all files"),
    ),
    IntentRule(
        IntentCategories.REPO_TREE,
        ("tree", "structure", "directory", "hierarchy", "repository", "full"),
        ("tree", "full tree", "show tree", "show the tree", "show full tree", "show a full tree", "show repository tree", "show project structure", "show repository structure", "show file structure", "show directory structure", "display project structure", "display repository structure", "show the file structure", "display the file structure", "display directory structure", "show the directory structure", "repository tree", "repository structure", "project structure", "repo tree"),
    ),
    IntentRule(
        IntentCategories.REPO_FIND,
        ("find", "locate", "file", "filename", "name"),
        ("find file", "locate file"),
    ),
    IntentRule(
        IntentCategories.REPO_SUMMARY,
        ("summary", "stats", "count", "repository", "files", "directories"),
        ("repo summary", "repository summary"),
    ),
    IntentRule(
        IntentCategories.FILE_READ,
        ("open", "read", "show", "file"),
        ("open file", "read file"),
    ),
    IntentRule(
        IntentCategories.SEARCH_TEXT,
        ("search", "find", "text"),
        ("search text", "find text"),
    ),
]
