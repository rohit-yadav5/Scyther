import subprocess

from rich.panel import Panel

from core.models import CommandStatus


class ModelCommand:
    @staticmethod
    def execute(context):
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        except Exception as e:
            context.console.print(f"Unable to load Ollama models: {e}", style="bold red")
            return
        lines = [line.strip() for line in result.stdout.splitlines()[1:] if line.strip()]
        if not lines:
            context.console.print("No Ollama models found", style="bold red")
            return
        models = [line.split()[0] for line in lines]
        context.console.print(
            Panel.fit(
                "\n".join([f"{i + 1}. {model}" for i, model in enumerate(models)]),
                title="Installed Ollama Models",
                border_style="green",
            )
        )
        return CommandStatus.HANDLED
