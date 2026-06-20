from pathlib import Path
import argparse
import re
import requests
from rich.console import Console
from rich.panel import Panel

OLLAMA_URL = "http://localhost:11434/api/chat"
PLANNER_MODEL = None
CODER_MODEL = None
REVIEWER_MODEL = None
CLASSIFIER_MODEL = None

console = Console()


class RepoScanner:
    IGNORE_DIRS = {
        ".git",
        "node_modules",
        "venv",
        ".venv",
        "dist",
        "build",
        "__pycache__",
    }

    @staticmethod
    def get_files(root: str):
        files = []

        for path in Path(root).rglob("*"):
            if any(part in RepoScanner.IGNORE_DIRS for part in path.parts):
                continue

            if path.is_file() and path.suffix in {
                ".py",
                ".js",
                ".ts",
                ".tsx",
                ".json",
                ".md",
            }:
                print(f"[Scanner] Found file: {path}", flush=True)
                files.append(path)

        return files


class OllamaClient:
    @staticmethod
    def chat(model: str, prompt: str):
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=300,
        )

        response.raise_for_status()
        return response.json()["message"]["content"]


class IntentClassifier:
    INTENTS = {
        "SYSTEM_COMMAND",
        "TOOL_ACTION",
        "FILE_OPERATION",
        "PROJECT_REVIEW",
        "PROJECT_QA",
        "CODE_CHANGE",
        "MULTI_STEP_TASK",
        "UNKNOWN",
    }

    @staticmethod
    def classify(prompt: str):
        classifier_prompt = f"""
You are an intent classifier.

Return ONLY one intent from:
SYSTEM_COMMAND
TOOL_ACTION
FILE_OPERATION
PROJECT_REVIEW
PROJECT_QA
CODE_CHANGE
MULTI_STEP_TASK
UNKNOWN

Examples:
User: add login page
Intent: CODE_CHANGE

User: create tests
Intent: CODE_CHANGE

User: explain authentication
Intent: PROJECT_QA

User: review project
Intent: PROJECT_REVIEW

User: list files
Intent: TOOL_ACTION

User: open README.md
Intent: FILE_OPERATION

User: {prompt}
Intent:
"""

        try:
            result = OllamaClient.chat(CLASSIFIER_MODEL, classifier_prompt)
        except Exception:
            return "UNKNOWN"
        intent = result.strip().split()[0].upper()
        return intent if intent in IntentClassifier.INTENTS else "UNKNOWN"


class IntentRouter:
    SYSTEM_COMMAND_PATTERNS = {"/help", "/model", "/display", "/permission", "/exit", "/bye"}
    TOOL_ACTION_PATTERNS = {
        "list files",
        "show files",
        "show directory",
        "pwd",
        "current directory",
    }
    FILE_OPERATION_PATTERNS = {
        r"^open\s+.+",
        r"^read\s+.+",
        r"^show file\s+.+",
    }
    PROJECT_REVIEW_PATTERNS = {
        "review project",
        "security review",
        "performance review",
        "audit codebase",
    }
    MULTI_STEP_TASK_PATTERNS = {
        "find bugs and fix them",
        "find all bugs and fix them",
        "review and fix",
        "fix all problems",
        "update readme",
        "generate report",
    }
    CODE_CHANGE_PATTERNS = {
        r"^(add|create|build|implement|fix|update|refactor|remove|replace|change|edit)\b",
        r"\b(login page|auth page|dashboard|api|endpoint|component|test|tests|feature)\b",
    }

    @staticmethod
    def classify(prompt: str, classifier_model: str | None = None):
        text = prompt.lower().strip()

        if text in IntentRouter.SYSTEM_COMMAND_PATTERNS:
            return "SYSTEM_COMMAND"

        if any(pattern in text for pattern in IntentRouter.TOOL_ACTION_PATTERNS):
            return "TOOL_ACTION"

        if any(re.search(pattern, text) for pattern in IntentRouter.FILE_OPERATION_PATTERNS):
            return "FILE_OPERATION"

        if any(pattern in text for pattern in IntentRouter.PROJECT_REVIEW_PATTERNS):
            return "PROJECT_REVIEW"

        if any(pattern in text for pattern in IntentRouter.MULTI_STEP_TASK_PATTERNS):
            return "MULTI_STEP_TASK"

        if any(re.search(pattern, text) for pattern in IntentRouter.CODE_CHANGE_PATTERNS):
            return "CODE_CHANGE"

        if classifier_model:
            return IntentClassifier.classify(prompt)

        return "UNKNOWN"


class ReviewAgent:
    @staticmethod
    def review_project(project_path: str):
        files = RepoScanner.get_files(project_path)

        print(f"[Scanner] Total files discovered: {len(files)}", flush=True)
        print("[Reviewer] Reading project files...", flush=True)

        project_content = []

        for file in files:
            try:
                print(f"[Reader] Loading: {file.name}", flush=True)
                content = file.read_text(encoding="utf-8")
                project_content.append(f"\nFILE: {file}\n{content[:5000]}")
            except Exception:
                pass

        print("[Context] Building review context...", flush=True)
        print(f"[Context] Loaded {len(project_content)} files", flush=True)
        print(f"[Reviewer] Sending request to {REVIEWER_MODEL}...", flush=True)

        prompt = f"""
Review this codebase.

Provide:
1. Critical Issues
2. Bugs
3. Security Problems
4. Performance Problems
5. Code Quality Issues

Codebase:
{''.join(project_content)}
"""

        return OllamaClient.chat(REVIEWER_MODEL, prompt)


class PlannerAgent:
    @staticmethod
    def create_plan(task: str):
        console.print(
            f"🟡 Planner Model: {PLANNER_MODEL}",
            style="bold yellow"
        )
        console.print(
            "🟡 Generating implementation plan...",
            style="yellow"
        )

        prompt = f"Create a step-by-step implementation plan.\n\nTask:\n{task}"
        return OllamaClient.chat(PLANNER_MODEL, prompt)


class CoderAgent:
    @staticmethod
    def generate_code(task: str, plan: str):
        console.print(
            f"🟢 Coder Model: {CODER_MODEL}",
            style="bold green"
        )
        console.print(
            "🟢 Generating solution...",
            style="green"
        )

        prompt = f"Task:\n{task}\n\nPlan:\n{plan}\n\nGenerate the implementation approach."
        return OllamaClient.chat(CODER_MODEL, prompt)


def run_review(args):
    print(ReviewAgent.review_project(args.path))


def run_edit(args):
    plan = PlannerAgent.create_plan(args.task)

    if getattr(args, "show_plan", True):
        console.print(
            Panel(
                plan,
                title="🟡 Plan",
                border_style="yellow",
            )
        )

    code = CoderAgent.generate_code(args.task, plan)

    if getattr(args, "show_solution", True):
        console.print(
            Panel(
                code,
                title="🟢 Generated Solution",
                border_style="green",
            )
        )


def run_classify(args):
    intent = IntentRouter.classify(args.prompt, args.classifier_model)
    print(intent)


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")

    review_parser = subparsers.add_parser("review")
    review_parser.add_argument("path")

    edit_parser = subparsers.add_parser("edit")
    edit_parser.add_argument("task")
    edit_parser.add_argument("--planner-model", default="qwen3:8b")
    edit_parser.add_argument("--coder-model", default="qwen2.5-coder:7b")
    edit_parser.add_argument("--classifier-model", default="qwen3.5:0.8b")
    edit_parser.add_argument("--show-plan", action="store_true")
    edit_parser.add_argument("--show-solution", action="store_true")

    classify_parser = subparsers.add_parser("classify")
    classify_parser.add_argument("prompt")
    classify_parser.add_argument("--classifier-model", default="qwen3.5:0.8b")

    args = parser.parse_args()

    global PLANNER_MODEL, CODER_MODEL, REVIEWER_MODEL, CLASSIFIER_MODEL

    PLANNER_MODEL = getattr(args, "planner_model", "qwen3:8b")
    CODER_MODEL = getattr(args, "coder_model", "qwen2.5-coder:7b")
    REVIEWER_MODEL = PLANNER_MODEL
    CLASSIFIER_MODEL = getattr(args, "classifier_model", "qwen3.5:0.8b")

    if args.command == "review":
        run_review(args)
    elif args.command == "edit":
        run_edit(args)
    elif args.command == "classify":
        run_classify(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
