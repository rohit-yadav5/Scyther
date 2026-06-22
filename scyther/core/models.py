from dataclasses import dataclass

class MultipleMatchesError(Exception):
    """Raised when a filename resolves to more than one file within the project root.

    Attributes:
        filename: The name that was searched for.
        matches: Relative paths of all matching files (sorted).
    """

    def __init__(self, filename: str, matches: list[str]):
        self.filename = filename
        self.matches = matches
        super().__init__(f"Multiple matches found for '{filename}'")


class DirectoryDeletionError(Exception):
    """Raised when a directory is deleted without the --force flag."""
    pass


class CommandStatus:
    HANDLED = "HANDLED"
    EXIT = "EXIT"
    NOT_HANDLED = "NOT_HANDLED"


class RuntimeContext:
    """Mutable runtime state passed to every command handler.

    Attributes:
        console:            Rich Console instance for all terminal output.
        current_permission: Active permission mode key (see core.config.PERMISSION_MODES).
        display_mode:       One of 'minimal', 'standard', 'verbose', 'debug'.
        project_root:       Absolute Path of the active project. All file
                            operations are confined to this directory.
    """

    def __init__(self, console, current_permission: str, display_mode: str, project_root):
        self.console = console
        self.current_permission = current_permission
        self.display_mode = display_mode
        self.project_root = project_root
        from scyther.services.config_service import ConfigService
        self.config = ConfigService(str(self.project_root))


@dataclass(slots=True)
class SymbolLocation:
    path: str
    line: int
    symbol: str


@dataclass(slots=True)
class FileDependency:
    source: str
    target: str
