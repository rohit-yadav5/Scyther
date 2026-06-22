import pytest
from pathlib import Path
from scyther.services.config_service import ConfigService


def test_config_service_defaults(tmp_path):
    service = ConfigService(str(tmp_path))
    assert service.get("default_tree_depth") == 3
    assert service.get("max_open_lines") == 500
    assert ".git" in service.ignored_dirs


def test_config_service_project_config(tmp_path):
    # Write custom project config
    project_config = tmp_path / ".scyther.toml"
    project_config.write_text(
        "default_tree_depth = 5\nignored_dirs = ['custom_dir']", encoding="utf-8"
    )

    service = ConfigService(str(tmp_path))
    # Overridden
    assert service.get("default_tree_depth") == 5
    # Default not overwritten remains
    assert service.get("max_open_lines") == 500
    # ignored_dirs is customized
    assert "custom_dir" in service.ignored_dirs
    assert ".git" not in service.ignored_dirs  # project config overrides ignored_dirs list


def test_config_service_user_config(tmp_path):
    # Write custom user config
    user_config_file = tmp_path / "user_config.toml"
    user_config_file.write_text(
        "max_open_lines = 1000\nignored_dirs = ['user_dir']", encoding="utf-8"
    )

    # Instantiate, then manually set user_config_path to bypass ~ expansion
    service = ConfigService(str(tmp_path))
    service.user_config_path = user_config_file
    # Reload config
    service.settings = service._load_config()

    assert service.get("max_open_lines") == 1000
    assert "user_dir" in service.ignored_dirs
    assert ".git" not in service.ignored_dirs
