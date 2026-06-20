from pathlib import Path

from ai.ollama_client import OllamaClient
from core.config import ACTIVE_MODELS


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
            if path.is_file() and path.suffix in {".py", ".js", ".ts", ".tsx", ".json", ".md"}:
                print(f"[Scanner] Found file: {path}", flush=True)
                files.append(path)
        return files


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
        print(f"[Reviewer] Sending request to {ACTIVE_MODELS['reviewer']}...", flush=True)
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
        return OllamaClient.chat(ACTIVE_MODELS["reviewer"], prompt)
