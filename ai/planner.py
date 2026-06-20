from rich.console import Console

from ai.ollama_client import OllamaClient
from core.config import ACTIVE_MODELS

console = Console()


class PlannerAgent:
    @staticmethod
    def create_plan(task: str):
        console.print(f"🟡 Planner Model: {ACTIVE_MODELS['planner']}", style="bold yellow")
        console.print("🟡 Generating implementation plan...", style="yellow")
        prompt = f"Create a step-by-step implementation plan.\n\nTask:\n{task}"
        return OllamaClient.chat(ACTIVE_MODELS["planner"], prompt)
