from commands.display_command import DisplayCommand
from commands.exit_command import ExitCommand
from commands.find_command import FindCommand
from commands.help_command import HelpCommand
from commands.list_command import ListCommand
from commands.open_command import OpenCommand
from commands.permission_command import PermissionCommand
from commands.search_command import SearchCommand
from commands.summary_command import SummaryCommand
from commands.tree_command import TreeCommand
from commands.create_command import CreateCommand
from commands.mkdir_command import MkdirCommand
from commands.write_command import WriteCommand
from commands.append_command import AppendCommand
from commands.replace_command import ReplaceCommand
from commands.delete_command import DeleteCommand
from commands.move_command import MoveCommand
from commands.copy_command import CopyCommand
from commands.stats_command import StatsCommand
from commands.git_status_command import GitStatusCommand
from commands.git_diff_command import GitDiffCommand
from commands.recent_command import RecentCommand
from commands.todo_command import TodoCommand
from core.models import CommandStatus
from routing.parser import Parser

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

        from core.command_registry import COMMANDS
        from permissions.access_control import AccessControl

        cmd_info = COMMANDS.get(parsed.name)
        if cmd_info and cmd_info.get("requires_write", False):
            if not AccessControl.can_execute(parsed.name, context, parsed.args):
                return CommandStatus.HANDLED

        return handler.execute(parsed.args, context)
