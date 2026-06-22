import sys
from core.models import CommandStatus
from core.version import __version__


class VersionCommand:
    """/version — display current version of Scyther and Python."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        context.console.print(f"Scyther v{__version__} (Python {py_ver})")
        return CommandStatus.HANDLED
