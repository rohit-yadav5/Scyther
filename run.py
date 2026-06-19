#!/usr/bin/env python3

# Scyther CLI entrypoint.
# After creating a launcher or installing through pyproject.toml,
# this file becomes the command executed when the user runs:
#
# scyther
#

import subprocess
from pathlib import Path
import sys
from rich.console import Console
from rich.panel import Panel

PERMISSION_MODES = {
    "1": "Read + Write (Current Directory)",
    "2": "Ask Before Edit (Current Directory)",
    "3": "Read Only (Current Directory)",
    "4": "Ask Before Edit (Anywhere)",
    "5": "Read Only (Anywhere)",
    "6": "Full Read + Write (Anywhere) [DANGER]",
}

CURRENT_PERMISSION = None

DISPLAY_MODE = "standard"

ACTIVE_MODELS = {
    "planner": "qwen3:8b",
    "coder": "qwen2.5-coder:7b",
    "reviewer": "qwen3:8b",
}

BASE_DIR = Path(__file__).parent
MAIN_FILE = BASE_DIR / "main.py"

console = Console()


class TerminalHelper:
    @staticmethod
    def select_permissions():
        global CURRENT_PERMISSION

        print("\n===================================")
        print(" Scyther Permission Mode")
        print("===================================")

        for key, value in PERMISSION_MODES.items():
            print(f"{key}. {value}")

        print("===================================")

        while True:
            choice = input("Select Permission Mode: ").strip()

            if choice in PERMISSION_MODES:
                CURRENT_PERMISSION = choice
                console.print(
                    Panel.fit(
                        PERMISSION_MODES[choice],
                        title="Permission Selected",
                        border_style="green",
                    )
                )
                print()
                break

            print("Invalid option")

    @staticmethod
    def display_settings():
        global DISPLAY_MODE

        console.print(
            Panel.fit(
                "1. Minimal\n2. Standard (Recommended)\n3. Verbose\n4. Debug",
                title="Display Mode",
                border_style="cyan",
            )
        )

        choice = input("display> ").strip()

        mapping = {
            "1": "minimal",
            "2": "standard",
            "3": "verbose",
            "4": "debug",
        }

        if choice in mapping:
            DISPLAY_MODE = mapping[choice]

            console.print(
                Panel.fit(
                    f"Active Mode: {DISPLAY_MODE.upper()}",
                    title="Display Updated",
                    border_style="green",
                )
            )

    @staticmethod
    def model_settings():
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True,
            )
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
                "\n".join(
                    [f"{i + 1}. {model}" for i, model in enumerate(models)]
                ),
                title="Installed Ollama Models",
                border_style="green",
            )
        )

        console.print("\nSelect target:")
        console.print("1. Planner")
        console.print("2. Coder")
        console.print("3. Reviewer")
        console.print("4. All Models")

        target = input("Target: ").strip()
        choice = input("Model number: ").strip()

        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(models):
            return

        selected_model = models[int(choice) - 1]

        if target == "1":
            ACTIVE_MODELS["planner"] = selected_model
        elif target == "2":
            ACTIVE_MODELS["coder"] = selected_model
        elif target == "3":
            ACTIVE_MODELS["reviewer"] = selected_model
        elif target == "4":
            ACTIVE_MODELS["planner"] = selected_model
            ACTIVE_MODELS["coder"] = selected_model
            ACTIVE_MODELS["reviewer"] = selected_model
        else:
            return

        console.print(
            Panel.fit(
                f"Planner : {ACTIVE_MODELS['planner']}\n"
                f"Coder : {ACTIVE_MODELS['coder']}\n"
                f"Reviewer : {ACTIVE_MODELS['reviewer']}",
                title="Active Models",
                border_style="yellow",
            )
        )

    @staticmethod
    def review_project():
        process = subprocess.Popen(
            [
                sys.executable,
                str(MAIN_FILE),
                "review",
                str(Path.cwd()),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        for line in process.stdout:
            if DISPLAY_MODE == "minimal":
                continue

            line = line.rstrip()

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
                if DISPLAY_MODE == "debug":
                    print(line)
                elif DISPLAY_MODE == "verbose":
                    print(line)

        process.wait()

        if DISPLAY_MODE == "minimal":
            console.print(
                Panel.fit(
                    "Task completed successfully",
                    title="Result",
                    border_style="green",
                )
            )

    @staticmethod
    def edit_project():
        task = input("What would you like to build? : ").strip()

        if not task:
            print("Task cannot be empty")
            return

        print("\n[Scyther] Creating implementation plan...")
        print("[Scyther] Planner agent started...")
        print("[Scyther] Waiting for coding model...\n")

        process = subprocess.Popen(
            [
                sys.executable,
                str(MAIN_FILE),
                "edit",
                task,
                "--planner-model",
                ACTIVE_MODELS["planner"],
                "--coder-model",
                ACTIVE_MODELS["coder"],
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        for line in process.stdout:
            if DISPLAY_MODE == "minimal":
                continue

            print(line, end="")

        process.wait()

        if DISPLAY_MODE == "minimal":
            console.print(
                Panel.fit(
                    "Task completed successfully",
                    title="Result",
                    border_style="green",
                )
            )

    @staticmethod
    def list_files():
        console.print(
            Panel.fit(
                "Listing files in current project",
                title="Tool Action",
                border_style="blue",
            )
        )

        for item in sorted(Path.cwd().iterdir()):
            if item.is_dir():
                console.print(f"📁 {item.name}", style="cyan")
            else:
                console.print(f"📄 {item.name}", style="green")

    @staticmethod
    def chat_shell():
        console.print(
            Panel.fit(
                f"Project: {Path.cwd()}\nPermission: {PERMISSION_MODES.get(CURRENT_PERMISSION)}\nDisplay Mode: {DISPLAY_MODE.upper()}\n\nCommands:\n  /help\n  /permission\n  /display\n  /model\n  /exit\n\nModels:\n  Planner  : {ACTIVE_MODELS['planner']}\n  Coder    : {ACTIVE_MODELS['coder']}\n  Reviewer : {ACTIVE_MODELS['reviewer']}",
                title="Scyther",
                border_style="cyan",
            )
        )
        print()

        while True:
            prompt = input("scyther> ").strip()

            if not prompt:
                continue

            if prompt in ["/exit", "/bye", "exit", "quit"]:
                print("Goodbye")
                break

            if prompt == "/help":
                console.print(
                    Panel.fit(
                        "/permission   Change permission mode\n/display      Display settings\n/model        Change Ollama model\n/help         Show help\n/exit         Exit Scyther\n/bye          Exit Scyther\n\nBuilt-in Actions\nlist files\nshow files",
                        title="Help",
                        border_style="blue",
                    )
                )
                continue

            if prompt == "/permission":
                TerminalHelper.select_permissions()
                continue

            if prompt == "/display":
                TerminalHelper.display_settings()
                continue

            if prompt == "/model":
                TerminalHelper.model_settings()
                continue

            if prompt.lower() in [
                "list files",
                "list all files",
                "show files",
                "show all files",
                "list all the files inside the folder",
            ]:
                TerminalHelper.list_files()
                continue

            if prompt.lower() == "review":
                TerminalHelper.review_project()
                continue

            task = prompt

            if DISPLAY_MODE in ["standard", "verbose", "debug"]:
                console.print(
                    Panel.fit(
                        f"Task: {task}",
                        title="Task Summary",
                        border_style="yellow",
                    )
                )

            if DISPLAY_MODE in ["verbose", "debug"]:
                console.print("🟡 Planner active", style="yellow")
                console.print("🟢 Coder waiting", style="green")
                console.print("🔵 Processing request", style="cyan")
                print()

            process = subprocess.Popen(
                [
                    sys.executable,
                    str(MAIN_FILE),
                    "edit",
                    task,
                    "--planner-model",
                    ACTIVE_MODELS["planner"],
                    "--coder-model",
                    ACTIVE_MODELS["coder"],
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            for line in process.stdout:
                if DISPLAY_MODE == "minimal":
                    continue

                line = line.rstrip()

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
                    if DISPLAY_MODE == "debug":
                        print(line)
                    elif DISPLAY_MODE == "verbose":
                        print(line)

            process.wait()

            if DISPLAY_MODE == "minimal":
                console.print(
                    Panel.fit(
                        "Task completed successfully",
                        title="Result",
                        border_style="green",
                    )
                )
            print()


def main():
    if CURRENT_PERMISSION is None:
        TerminalHelper.select_permissions()

    TerminalHelper.chat_shell()


if __name__ == "__main__":
    main()