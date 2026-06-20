from rich.console import Console

from ai.ollama_client import OllamaClient
from core.config import ACTIVE_MODELS

console = Console()


class CoderAgent:
    @staticmethod
    def generate_code(task: str, plan: str):
        console.print(f"🟢 Coder Model: {ACTIVE_MODELS['coder']}", style="bold green")
        console.print("🟢 Generating solution...", style="green")
        prompt = f"Task:\n{task}\n\nPlan:\n{plan}\n\nGenerate the implementation approach."
        return OllamaClient.chat(ACTIVE_MODELS["coder"], prompt)
