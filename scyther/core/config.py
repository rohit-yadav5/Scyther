PERMISSION_MODES = {
    "1": "Read + Write (Current Directory)",
    "2": "Ask Before Edit (Current Directory)",
    "3": "Read Only (Current Directory)",
    "4": "Ask Before Edit (Anywhere)",
    "5": "Read Only (Anywhere)",
    "6": "Full Read + Write (Anywhere) [DANGER]",
}

CURRENT_PERMISSION = "3"
DISPLAY_MODE = "standard"

# Directories ignored by all project-scoped operations (tree, list, find, open, search).
# Matching is applied against relative path segments — any component of a path that
# matches an entry here causes that path to be excluded, regardless of depth.
IGNORED_DIRS: frozenset[str] = frozenset({
    ".git",
    ".venv",
    ".cache",
    ".pytest_cache",
    "__pycache__",
    "pycache",
    "node_modules",
    "dist",
    "build",
})
