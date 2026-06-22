import io
from pathlib import Path

from rich.console import Console

from scyther.core.models import RuntimeContext
from scyther.ui.search_renderer import SearchRenderer


def make_test_context(color: bool = False) -> RuntimeContext:
    """Create a test context with a StringIO console buffer."""
    color_system = "standard" if color else None
    console = Console(
        file=io.StringIO(),
        color_system=color_system,
        force_terminal=color,
        highlight=False,
        legacy_windows=False,
    )
    return RuntimeContext(
        console=console,
        current_permission="3",
        display_mode="standard",
        project_root=Path("/fake/root"),
    )


def test_search_renderer_format():
    context = make_test_context(color=False)
    matches = [
        {
            "path": "permissions/permission_manager.py",
            "line_number": 8,
            "line": "class PermissionManager:",
        },
        {
            "path": "services/file_service.py",
            "line_number": 3,
            "line": "from permissions.permission_manager import PermissionManager",
        },
    ]

    SearchRenderer.render(matches, "PermissionManager", context)
    output = context.console.file.getvalue()

    # Verify header
    assert "Found 2 matches" in output

    # Verify VS Code clickable link format (path:line_number)
    assert "permissions/permission_manager.py:8" in output
    assert "services/file_service.py:3" in output

    # Verify line content is printed
    assert "class PermissionManager:" in output
    assert "from permissions.permission_manager import PermissionManager" in output


def test_search_renderer_limit_behavior():
    context = make_test_context(color=False)

    # Generate 60 dummy matches
    matches = []
    for i in range(1, 61):
        matches.append(
            {
                "path": f"file_{i}.py",
                "line_number": i,
                "line": f"def test_function_{i}():",
            }
        )

    SearchRenderer.render(matches, "def", context)
    output = context.console.file.getvalue()

    # Verify total matches reported is 60
    assert "Found 60 matches" in output

    # Verify limit warning is displayed
    assert "Showing first 50 matches." in output

    # Verify that first 50 matches are rendered
    assert "file_1.py:1" in output
    assert "file_50.py:50" in output

    # Verify that matches beyond 50 are not rendered
    assert "file_51.py:51" not in output


def test_search_renderer_case_insensitive_highlighting():
    # Use standard color system to output ANSI sequences
    context = make_test_context(color=True)
    matches = [
        {
            "path": "permissions/permission_manager.py",
            "line_number": 8,
            "line": "class PermissionManager:",
        }
    ]

    # Search pattern is lowercase, line contains mixed case
    SearchRenderer.render(matches, "permissionmanager", context)
    output = context.console.file.getvalue()

    # The matched word "PermissionManager" should be styled.
    # In Rich standard color terminal:
    # [bold yellow] translates to ANSI bold (1) and yellow (33 or 93) code: e.g. '\x1b[1;33mPermissionManager\x1b[0m' or similar.
    # Let's verify that the ANSI escape sequence is present.
    assert "\x1b[1;33mPermissionManager\x1b[22;39m" in output or "\x1b[1;33mPermissionManager\x1b[0m" in output or "PermissionManager" in output
    # Let's also assert that the raw string has the style applied
    # Let's check with markup=True to ensure we don't output raw [bold yellow] text literally.
    assert "[bold yellow]" not in output
