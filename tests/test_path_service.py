import pytest
from pathlib import Path
from core.errors import PermissionDeniedError
from services.path_service import PathService


def test_path_service_normalize(tmp_path):
    project_root = tmp_path
    service = PathService(str(project_root))

    # Relative path
    rel_path = "src/main.py"
    normalized = service.normalize(rel_path)
    assert normalized == (project_root / "src/main.py").resolve()

    # Absolute path
    abs_path = str((project_root / "test.txt").resolve())
    normalized_abs = service.normalize(abs_path)
    assert normalized_abs == Path(abs_path)


def test_path_service_is_within_root(tmp_path):
    project_root = tmp_path
    service = PathService(str(project_root))

    # Inside
    assert service.is_within_root(project_root / "file.txt")
    assert service.is_within_root(project_root / "sub/file.txt")
    assert service.is_within_root(project_root)

    # Outside
    assert not service.is_within_root(project_root.parent / "other_file.txt")


def test_path_service_is_ignored(tmp_path):
    project_root = tmp_path
    ignored_dirs = frozenset([".git", "venv", "node_modules"])
    service = PathService(str(project_root), ignored_dirs=ignored_dirs)

    # Normal files
    assert not service.is_ignored(project_root / "src/main.py")
    assert not service.is_ignored(project_root / "index.js")

    # Ignored files/dirs
    assert service.is_ignored(project_root / ".git/config")
    assert service.is_ignored(project_root / "venv/bin/python")
    assert service.is_ignored(project_root / "node_modules/lodash/index.js")

    # Outside root is treated as ignored/inaccessible
    assert service.is_ignored(project_root.parent / "other.txt")


def test_path_service_resolve_and_validate(tmp_path):
    project_root = tmp_path
    ignored_dirs = frozenset(["venv"])
    service = PathService(str(project_root), ignored_dirs=ignored_dirs)

    # Valid
    resolved = service.resolve_and_validate("src/main.py")
    assert resolved == (project_root / "src/main.py").resolve()

    # Outside root throws PermissionDeniedError
    with pytest.raises(PermissionDeniedError) as exc_info:
        service.resolve_and_validate("../outside.txt")
    assert "outside project root" in str(exc_info.value)

    # Inside ignored directory throws PermissionDeniedError
    with pytest.raises(PermissionDeniedError) as exc_info:
        service.resolve_and_validate("venv/lib/package.py")
    assert "inside an ignored directory" in str(exc_info.value)

    # If check_ignored=False, ignored directory check is bypassed
    resolved_ignored = service.resolve_and_validate("venv/lib/package.py", check_ignored=False)
    assert resolved_ignored == (project_root / "venv/lib/package.py").resolve()
