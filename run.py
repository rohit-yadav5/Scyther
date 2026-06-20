#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from core.config import CURRENT_PERMISSION, DISPLAY_MODE, PERMISSION_MODES
from core.models import CommandStatus, RuntimeContext
from services.file_service import FileService
from permissions.permission_manager import PermissionManager
from services.repo_service import RepoService
from routing.command_router import CommandRouter
from routing.intent_router import IntentRouter
from ui.file_renderer import FileRenderer
from ui.repo_renderer import RepoRenderer

BASE_DIR = Path(__file__).parent
console = Console()


class TerminalHelper:
    context = RuntimeContext(
        console=console,
        current_permission=CURRENT_PERMISSION,
        display_mode=DISPLAY_MODE,
        base_dir=BASE_DIR,
    )
    permission_manager = PermissionManager(context)
    repo_service = RepoService(str(BASE_DIR))
    file_service = FileService(str(BASE_DIR))

    @staticmethod
    def select_permissions():
        from commands.permission_command import PermissionCommand

        return PermissionCommand.execute(TerminalHelper.context)

    @staticmethod
    def display_settings():
        from commands.display_command import DisplayCommand

        return DisplayCommand.execute(TerminalHelper.context)

    @staticmethod
    def list_files():
        result = TerminalHelper.repo_service.list_files()
        RepoRenderer.render_file_list(result["files"])

    @staticmethod
    def show_tree(max_depth=None):
        tree = TerminalHelper.repo_service.show_tree(max_depth=max_depth)
        RepoRenderer.render_tree(tree)

    @staticmethod
    def find_file(filename: str):
        matches = TerminalHelper.repo_service.find_file(filename)
        for match in matches:
            console.print(match)

    @staticmethod
    def repo_summary():
        summary = TerminalHelper.repo_service.repo_summary()
        RepoRenderer.render_summary(summary)

    @staticmethod
    def read_file(filename: str):
        try:
            result = TerminalHelper.file_service.read_file(filename)
        except FileNotFoundError as exc:
            FileRenderer.render_error(str(exc))
            return
        except IsADirectoryError as exc:
            FileRenderer.render_error(str(exc))
            return

        FileRenderer.render_file(
            {
                "name": Path(result["path"]).name,
                "path": result["path"],
                "content": result["content"],
            }
        )

    @staticmethod
    def detect_intent(prompt: str):
        return IntentRouter.inspect(prompt)

    @staticmethod
    def chat_shell():
        console.print(
            Panel.fit(
                f"Project: {Path.cwd()}\nPermission Mode: {TerminalHelper.context.current_permission}\nDisplay Mode: {TerminalHelper.context.display_mode.upper()}\n\nAvailable Commands:\n  /help\n  /permission\n  /display\n  /exit",
                title="Scyther",
                border_style="cyan",
            )
        )
        print()

        while True:
            prompt = input("scyther> ").strip()
            if not prompt:
                continue

            command_result = CommandRouter.route(prompt, TerminalHelper.context)
            if command_result == CommandStatus.EXIT:
                print("Goodbye")
                break
            if command_result == CommandStatus.HANDLED:
                continue
            if command_result != CommandStatus.NOT_HANDLED:
                continue

            intent_result = TerminalHelper.detect_intent(prompt)
            intent = intent_result.intent
            if intent == "SYSTEM_COMMAND":
                continue
            if intent in ["REPO_LIST", "TOOL_ACTION"]:
                TerminalHelper.list_files()
                continue
            if intent == "REPO_TREE":
                TerminalHelper.show_tree(max_depth=intent_result.extracted_entities.get("depth"))
                continue
            if intent == "REPO_FIND":
                parts = prompt.split(maxsplit=2)
                filename = parts[2] if len(parts) >= 3 else ""
                if filename:
                    TerminalHelper.find_file(filename)
                continue
            if intent == "REPO_SUMMARY":
                TerminalHelper.repo_summary()
                continue
            if intent == "FILE_READ":
                filenames = intent_result.extracted_entities.get("filenames", [])
                filename = filenames[0] if filenames else prompt.split(maxsplit=1)[1] if len(prompt.split(maxsplit=1)) > 1 else ""
                if filename:
                    TerminalHelper.read_file(filename)
                else:
                    FileRenderer.render_error("File not found: ")
                continue

            console.print(f"Unknown command: {prompt}")

            if TerminalHelper.context.display_mode == "debug":
                console.print(
                    f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] No deterministic task handler available for: {prompt}",
                    style="bright_black",
                )


def main():
    TerminalHelper.chat_shell()


if __name__ == "__main__":
    main()
