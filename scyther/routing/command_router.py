from scyther.commands.display_command import DisplayCommand
from scyther.commands.exit_command import ExitCommand
from scyther.commands.find_command import FindCommand
from scyther.commands.help_command import HelpCommand
from scyther.commands.list_command import ListCommand
from scyther.commands.open_command import OpenCommand
from scyther.commands.permission_command import PermissionCommand
from scyther.commands.search_command import SearchCommand
from scyther.commands.summary_command import SummaryCommand
from scyther.commands.tree_command import TreeCommand
from scyther.commands.create_command import CreateCommand
from scyther.commands.mkdir_command import MkdirCommand
from scyther.commands.write_command import WriteCommand
from scyther.commands.append_command import AppendCommand
from scyther.commands.replace_command import ReplaceCommand
from scyther.commands.delete_command import DeleteCommand
from scyther.commands.move_command import MoveCommand
from scyther.commands.copy_command import CopyCommand
from scyther.commands.stats_command import StatsCommand
from scyther.commands.git_status_command import GitStatusCommand
from scyther.commands.git_diff_command import GitDiffCommand
from scyther.commands.recent_command import RecentCommand
from scyther.commands.todo_command import TodoCommand
from scyther.commands.where_command import WhereCommand
from scyther.commands.refs_command import RefsCommand
from scyther.commands.deps_command import DepsCommand
from scyther.commands.largest_command import LargestCommand
from scyther.commands.about_command import AboutCommand
from scyther.commands.version_command import VersionCommand
from scyther.commands.doctor_command import DoctorCommand
from scyther.commands.config_command import ConfigCommand
from scyther.core.models import CommandStatus
from scyther.routing.parser import Parser

# Registry: maps command name → handler class.
# To add a new command: add one entry here + create the command class.
_REGISTRY = {
    "/help":       HelpCommand,
    "/exit":       ExitCommand,
    "/bye":        ExitCommand,
    "/list":       ListCommand,
    "/tree":       TreeCommand,
    "/open":       OpenCommand,
    "/find":       FindCommand,
    "/search":     SearchCommand,
    "/summary":    SummaryCommand,
    "/permission": PermissionCommand,
    "/display":    DisplayCommand,
    "/create":     CreateCommand,
    "/mkdir":      MkdirCommand,
    "/write":      WriteCommand,
    "/append":     AppendCommand,
    "/replace":    ReplaceCommand,
    "/delete":     DeleteCommand,
    "/move":       MoveCommand,
    "/copy":       CopyCommand,
    "/stats":      StatsCommand,
    "/git-status": GitStatusCommand,
    "/git-diff":   GitDiffCommand,
    "/recent":     RecentCommand,
    "/todo":       TodoCommand,
    "/where":      WhereCommand,
    "/refs":       RefsCommand,
    "/deps":       DepsCommand,
    "/largest":    LargestCommand,
    "/about":      AboutCommand,
    "/version":    VersionCommand,
    "/doctor":     DoctorCommand,
    "/config":     ConfigCommand,
}


class CommandRouter:
    @staticmethod
    def route(raw: str, context) -> CommandStatus:
        try:
            parsed = Parser.parse(raw)
        except ValueError as exc:
            if "No closing quotation" in str(exc) or "closing quotation" in str(exc):
                context.console.print("Parser error: unmatched quote")
            else:
                context.console.print(f"Parser error: {exc}")
            return CommandStatus.HANDLED

        handler = _REGISTRY.get(parsed.name)
        if handler is None:
            return CommandStatus.NOT_HANDLED

        from scyther.core.command_registry import COMMANDS
        from scyther.permissions.access_control import AccessControl

        cmd_info = COMMANDS.get(parsed.name)
        if cmd_info and cmd_info.get("requires_write", False):
            if not AccessControl.can_execute(parsed.name, context, parsed.args):
                return CommandStatus.HANDLED

        return handler.execute(parsed.args, context)
