from rich.panel import Panel

from scyther.core.models import CommandStatus
from scyther.core.command_registry import COMMANDS


class HelpCommand:
    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        if args:
            cmd_name = args[0]
            if not cmd_name.startswith("/"):
                cmd_name = "/" + cmd_name
            
            if cmd_name in COMMANDS:
                info = COMMANDS[cmd_name]
                dangerous_str = "Yes" if info.get("dangerous", False) else "No"
                context.console.print(f"Command: {cmd_name}\n")
                context.console.print("Usage:")
                context.console.print(f"{info['usage']}\n")
                context.console.print("Description:")
                context.console.print(f"{info['description']}\n")
                context.console.print("Dangerous:")
                context.console.print(f"{dangerous_str}\n")
                context.console.print("Category:")
                context.console.print(f"{info['category']}")
            else:
                context.console.print(f"[red]No help available for command: {cmd_name}[/red]")
            return CommandStatus.HANDLED

        # Group commands by category
        categories = {
            "Repository": [],
            "Modification": [],
            "Git": [],
            "Release": [],
            "System": [],
        }
        for name, info in COMMANDS.items():
            cat = info.get("category", "System")
            if cat in categories:
                categories[cat].append((name, info))
            else:
                categories.setdefault(cat, []).append((name, info))

        for cat_name, cmd_list in categories.items():
            if not cmd_list:
                continue
            content_parts = []
            for name, info in cmd_list:
                usage = info["usage"]
                desc = info["description"]
                dangerous = info.get("dangerous", False)
                
                part = f"[bold cyan]{usage}[/bold cyan]\n{desc}"
                if dangerous:
                    part += "\n[bold red]⚠ Dangerous[/bold red]"
                content_parts.append(part)
            
            panel_content = "\n\n".join(content_parts)
            
            border_style = "blue"
            if cat_name == "Repository":
                border_style = "cyan"
            elif cat_name == "Modification":
                border_style = "yellow"
            elif cat_name == "Git":
                border_style = "magenta"
            elif cat_name == "Release":
                border_style = "blue"
            elif cat_name == "System":
                border_style = "green"
                
            context.console.print(
                Panel.fit(
                    panel_content,
                    title=f"{cat_name} Commands",
                    border_style=border_style
                )
            )
        return CommandStatus.HANDLED
