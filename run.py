#!/usr/bin/env python3

import subprocess
from datetime import datetime
from pathlib import Path
import sys

from rich.console import Console
from rich.panel import Panel

from core.config import ACTIVE_MODELS, CURRENT_PERMISSION, DISPLAY_MODE, PERMISSION_MODES
from core.models import CommandStatus, RuntimeContext
from routing.command_router import CommandRouter
from routing.intent_router import IntentRouter

BASE_DIR = Path(__file__).parent
MAIN_FILE = BASE_DIR / "main.py"

console = Console()


class TerminalHelper:
    context = RuntimeContext(
        console=console,
        current_permission=CURRENT_PERMISSION,
        display_mode=DISPLAY_MODE,
        active_models=ACTIVE_MODELS,
        base_dir=BASE_DIR,
        main_file=MAIN_FILE,
    )

    @staticmethod
    def select_permissions():
        print("\n===================================")
        print(" Scyther Permission Mode")
        print("===================================")
        for key, value in PERMISSION_MODES.items():
            print(f"{key}. {value}")
        print("===================================")
        while True:
            choice = input("Select Permission Mode: ").strip()
            if choice in PERMISSION_MODES:
                TerminalHelper.context.current_permission = choice
                console.print(
                    Panel.fit(PERMISSION_MODES[choice], title="Permission Selected", border_style="green")
                )
                print()
                break
            print("Invalid option")

    @staticmethod
    def display_settings():
        console.print(
            Panel.fit(
                "1. Minimal\n2. Standard (Recommended)\n3. Verbose\n4. Debug",
                title="Display Mode",
                border_style="cyan",
            )
        )
        choice = input("display> ").strip()
        mapping = {"1": "minimal", "2": "standard", "3": "verbose", "4": "debug"}
        if choice in mapping:
            TerminalHelper.context.display_mode = mapping[choice]
            console.print(
                Panel.fit(
                    f"Active Mode: {TerminalHelper.context.display_mode.upper()}",
                    title="Display Updated",
                    border_style="green",
                )
            )

    @staticmethod
    def model_settings():
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        except Exception as e:
            console.print(f"Unable to load Ollama models: {e}", style="bold red")
            return

        lines = [line.strip() for line in result.stdout.splitlines()[1:] if line.strip()]
        if not lines:
            console.print("No Ollama models found", style="bold red")
            return

        models = [line.split()[0] for line in lines]
        console.print(
            Panel.fit(
                "\n".join([f"{i + 1}. {model}" for i, model in enumerate(models)]),
                title="Installed Ollama Models",
                border_style="green",
            )
        )
        console.print("\nSelect target:")
        console.print("1. Planner")
        console.print("2. Coder")
        console.print("3. Reviewer")
        console.print("4. Classifier")
        console.print("5. All Models")
        target = input("Target: ").strip()
        choice = input("Model number: ").strip()
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(models):
            return
        selected_model = models[int(choice) - 1]
        if target == "1":
            TerminalHelper.context.active_models["planner"] = selected_model
        elif target == "2":
            TerminalHelper.context.active_models["coder"] = selected_model
        elif target == "3":
            TerminalHelper.context.active_models["reviewer"] = selected_model
        elif target == "4":
            TerminalHelper.context.active_models["classifier"] = selected_model
        elif target == "5":
            TerminalHelper.context.active_models["planner"] = selected_model
            TerminalHelper.context.active_models["coder"] = selected_model
            TerminalHelper.context.active_models["reviewer"] = selected_model
        else:
            return
        console.print(
            Panel.fit(
                f"Planner : {TerminalHelper.context.active_models['planner']}\n"
                f"Coder : {TerminalHelper.context.active_models['coder']}\n"
                f"Reviewer : {TerminalHelper.context.active_models['reviewer']}\n"
                f"Classifier : {TerminalHelper.context.active_models['classifier']}",
                title="Active Models",
                border_style="yellow",
            )
        )

    @staticmethod
    def review_project():
        start_time = datetime.now()
        if TerminalHelper.context.display_mode == "debug":
            console.print(
                f"[{start_time.strftime('%H:%M:%S.%f')[:-3]}] Launching review on {Path.cwd()}",
                style="bright_black",
            )
        process = subprocess.Popen(
            [sys.executable, str(MAIN_FILE), "review", str(Path.cwd())],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        for line in process.stdout:
            if TerminalHelper.context.display_mode == "minimal":
                continue
            line = line.rstrip()
            if TerminalHelper.context.display_mode == "debug":
                line = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {line}"
            if "[Planner]" in line:
                console.print(line, style="bold yellow")
            elif "[Coder]" in line:
                console.print(line, style="bold green")
            elif "[Reviewer]" in line:
                console.print(line, style="bold magenta")
            elif "[Scanner]" in line:
                console.print(line, style="bold cyan")
            elif "[Reader]" in line:
                console.print(line, style="blue")
            elif "[Context]" in line:
                console.print(line, style="bright_blue")
            else:
                if TerminalHelper.context.display_mode in ["debug", "verbose"]:
                    print(line)
        process.wait()
        if TerminalHelper.context.display_mode == "debug":
            duration = (datetime.now() - start_time).total_seconds()
            console.print(
                f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Review completed in {duration:.2f}s",
                style="bright_black",
            )

    @staticmethod
    def edit_project(task: str):
        start_time = datetime.now()
        if not task:
            print("Task cannot be empty")
            return
        process = subprocess.Popen(
            [
                sys.executable,
                str(MAIN_FILE),
                "edit",
                task,
                "--planner-model",
                TerminalHelper.context.active_models["planner"],
                "--coder-model",
                TerminalHelper.context.active_models["coder"],
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        for line in process.stdout:
            if TerminalHelper.context.display_mode == "minimal":
                continue
            print(line, end="")
        process.wait()
        if TerminalHelper.context.display_mode == "debug":
            duration = (datetime.now() - start_time).total_seconds()
            console.print(
                f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Edit completed in {duration:.2f}s",
                style="bright_black",
            )

    @staticmethod
    def list_files():
        console.print(
            Panel.fit("Listing files in current project", title="Tool Action", border_style="blue")
        )
        for item in sorted(Path.cwd().iterdir()):
            if item.is_dir():
                console.print(f"📁 {item.name}", style="cyan")
            else:
                console.print(f"📄 {item.name}", style="green")

    @staticmethod
    def detect_intent(prompt: str):
        return IntentRouter.route(prompt)

    @staticmethod
    def chat_shell():
        console.print(
            Panel.fit(
                f"Project: {Path.cwd()}\nPermission: {PERMISSION_MODES.get(TerminalHelper.context.current_permission)}\nDisplay Mode: {TerminalHelper.context.display_mode.upper()}\n\nCommands:\n  /help\n  /permission\n  /display\n  /model\n  /exit\n\nModels:\n  Planner  : {TerminalHelper.context.active_models['planner']}\n  Coder    : {TerminalHelper.context.active_models['coder']}\n  Reviewer : {TerminalHelper.context.active_models['reviewer']}\n  Classifier : {TerminalHelper.context.active_models['classifier']}",
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
            if command_result == CommandStatus.NOT_HANDLED:
                pass
            if prompt.lower() in [
                "list files",
                "list all files",
                "show files",
                "show all files",
                "list all the files inside the folder",
            ]:
                TerminalHelper.list_files()
                continue
            intent = TerminalHelper.detect_intent(prompt)
            if TerminalHelper.context.display_mode == "debug":
                console.print(
                    f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Intent Detection Complete -> {intent}",
                    style="bright_black",
                )
            if intent == "PROJECT_REVIEW":
                TerminalHelper.review_project()
                continue
            if TerminalHelper.context.display_mode in ["verbose", "debug"]:
                console.print(f"Detected Intent: {intent}", style="bold cyan")
            if TerminalHelper.context.display_mode in ["standard", "verbose", "debug"]:
                console.print(Panel.fit(f"Task: {prompt}", title="Task Summary", border_style="yellow"))
            if TerminalHelper.context.display_mode in ["verbose", "debug"]:
                console.print("🟡 Planner active", style="yellow")
                console.print("🟢 Coder waiting", style="green")
                console.print("🔵 Processing request", style="cyan")
                print()
            if TerminalHelper.context.display_mode == "debug":
                console.print(
                    f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Launching Planner={TerminalHelper.context.active_models['planner']} | Coder={TerminalHelper.context.active_models['coder']}",
                    style="bright_black",
                )
            start_time = datetime.now()
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(MAIN_FILE),
                    "edit",
                    prompt,
                    "--planner-model",
                    TerminalHelper.context.active_models["planner"],
                    "--coder-model",
                    TerminalHelper.context.active_models["coder"],
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            for line in process.stdout:
                if TerminalHelper.context.display_mode == "minimal":
                    continue
                line = line.rstrip()
                if TerminalHelper.context.display_mode == "debug":
                    line = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {line}"
                if "[Planner]" in line:
                    console.print(line, style="bold yellow")
                elif "[Coder]" in line:
                    console.print(line, style="bold green")
                elif "[Reviewer]" in line:
                    console.print(line, style="bold magenta")
                elif "[Scanner]" in line:
                    console.print(line, style="bold cyan")
                elif "[Reader]" in line:
                    console.print(line, style="blue")
                elif "[Context]" in line:
                    console.print(line, style="bright_blue")
                else:
                    if TerminalHelper.context.display_mode == "debug":
                        print(line)
                    elif TerminalHelper.context.display_mode == "verbose":
                        print(line)
            process.wait()
            if TerminalHelper.context.display_mode == "debug":
                duration = (datetime.now() - start_time).total_seconds()
                console.print(
                    f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Process completed in {duration:.2f}s",
                    style="bright_black",
                )
            print()


def main():
    TerminalHelper.chat_shell()


if __name__ == "__main__":
    main()
