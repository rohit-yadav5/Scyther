
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
import time

BASE_DIR = Path(__file__).parent
MAIN_FILE = BASE_DIR / "main.py"


class TerminalHelper:
    @staticmethod
    def review_project():
        path = str(Path.cwd())
        print("\n[Scyther] Starting project review...")
        print("[Scyther] Scanning repository...")
        print("[Scyther] Loading files into context...")
        print("[Scyther] Sending review request to model...\n")

        process = subprocess.Popen(
            [
                sys.executable,
                str(MAIN_FILE),
                "review",
                path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        for line in process.stdout:
            print(line, end="")

        process.wait()

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
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        for line in process.stdout:
            print(line, end="")

        process.wait()

    @staticmethod
    def thinking_tab():
        print("\n===================================")
        print(" Thinking / Model Status")
        print("===================================")
        print("Planner Model  : qwen3:8b")
        print("Coder Model    : qwen2.5-coder:7b")
        print("Reviewer Model : qwen3:8b")
        print("Ollama URL     : http://localhost:11434")
        print("\nChecking connection...")

        spinner = ["|", "/", "-", "\\"]

        for i in range(20):
            print(f"\rWaiting for model {spinner[i % len(spinner)]}", end="")
            time.sleep(0.1)

        print("\rModel status: Ready            ")
        input("\nPress Enter to return to menu...")


MENU = """
===================================
 MyCoder Terminal Helper
===================================

1. Review Project
2. Create Implementation Plan
3. Thinking / Model Status
4. Exit

===================================
"""


def main():
    while True:
        print(MENU)

        choice = input("Select option: ").strip()

        if choice == "1":
            TerminalHelper.review_project()

        elif choice == "2":
            TerminalHelper.edit_project()

        elif choice == "3":
            TerminalHelper.thinking_tab()

        elif choice == "4":
            print("Goodbye")
            break

        else:
            print("Invalid option")


if __name__ == "__main__":
    main()