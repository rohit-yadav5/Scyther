class ScytherError(Exception):
    """Base exception class for all Scyther errors."""
    pass


class CommandError(ScytherError):
    """Raised when a command fails to execute properly."""
    pass


class InvalidArgumentError(CommandError, ValueError):
    """Raised when command arguments are invalid or missing."""
    pass


class PermissionDeniedError(CommandError, PermissionError):
    """Raised when an operation violates permission boundaries."""
    pass


class PathResolutionError(CommandError, FileNotFoundError):
    """Raised when a file or directory path cannot be resolved or is invalid."""
    pass


class ConfigurationError(ScytherError):
    """Raised when configuration parsing or loading fails."""
    pass
