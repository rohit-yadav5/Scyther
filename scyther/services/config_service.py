import os
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

DEFAULT_IGNORED_DIRS = [
    ".git",
    ".venv",
    ".cache",
    ".pytest_cache",
    "__pycache__",
    "pycache",
    "node_modules",
    "dist",
    "build",
]


class ConfigService:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.user_config_path = Path("~/.scyther/config.toml").expanduser()
        self.project_config_path = self.project_root / ".scyther.toml"
        self.settings = self._load_config()

    def _load_config(self) -> dict:
        # 1. Defaults
        settings = {
            "ignored_dirs": list(DEFAULT_IGNORED_DIRS),
            "default_tree_depth": 3,
            "max_open_lines": 500,
        }

        # Helper to load and parse a TOML file
        def load_toml(path: Path) -> dict:
            if not path.is_file():
                return {}
            try:
                with path.open("rb") as f:
                    return tomllib.load(f)
            except Exception:
                return {}

        # 2. Project Config
        project_data = load_toml(self.project_config_path)
        if project_data:
            settings.update(project_data)

        # 3. User Config
        user_data = load_toml(self.user_config_path)
        if user_data:
            settings.update(user_data)

        return settings

    def get(self, key: str, default=None):
        return self.settings.get(key, default)

    @property
    def ignored_dirs(self) -> frozenset[str]:
        return frozenset(self.settings["ignored_dirs"])
