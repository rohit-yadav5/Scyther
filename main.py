

from pathlib import Path
import argparse
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
PLANNER_MODEL = "qwen3:8b"
CODER_MODEL = "qwen2.5-coder:7b"
REVIEWER_MODEL = "qwen3:8b"


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
                files.append(path)

        return files


class OllamaClient:
    @staticmethod
    def chat(model: str, prompt: str):
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "stream": False,
            },
            timeout=300,
        )

        response.raise_for_status()

        return response.json()["message"]["content"]


class ReviewAgent:
    @staticmethod
    def review_project(project_path: str):
        files = RepoScanner.get_files(project_path)

        project_content = []

        for file in files:
            try:
                content = file.read_text(encoding="utf-8")
                project_content.append(
                    f"\nFILE: {file}\n{content[:5000]}"
                )
            except Exception:
                pass

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
        prompt = f"""
Create a step-by-step implementation plan.

Task:
{task}
"""

        return OllamaClient.chat(PLANNER_MODEL, prompt)


class CoderAgent:
    @staticmethod
    def generate_code(task: str, plan: str):
        prompt = f"""
Task:
{task}

Plan:
{plan}

Generate the implementation approach.
"""

        return OllamaClient.chat(CODER_MODEL, prompt)


def run_review(args):
    result = ReviewAgent.review_project(args.path)
    print(result)


def run_edit(args):
    plan = PlannerAgent.create_plan(args.task)

    print("\n=== PLAN ===\n")
    print(plan)

    code = CoderAgent.generate_code(args.task, plan)

    print("\n=== GENERATED OUTPUT ===\n")
    print(code)


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")

    review_parser = subparsers.add_parser("review")
    review_parser.add_argument("path")

    edit_parser = subparsers.add_parser("edit")
    edit_parser.add_argument("task")

    args = parser.parse_args()

    if args.command == "review":
        run_review(args)

    elif args.command == "edit":
        run_edit(args)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()