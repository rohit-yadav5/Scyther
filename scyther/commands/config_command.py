from scyther.core.models import CommandStatus


class ConfigCommand:
    """/config — display active settings and loaded config files."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        cfg = context.config
        user_exists = cfg.user_config_path.is_file()
        proj_exists = cfg.project_config_path.is_file()

        context.console.print("Loaded Configs:")
        context.console.print(f"  - Global: {cfg.user_config_path} ({'Found' if user_exists else 'Not found'})")
        context.console.print(f"  - Project: {cfg.project_config_path} ({'Found' if proj_exists else 'Not found'})")

        context.console.print("Settings:")
        # Sort ignored_dirs for consistent, clean output
        ignored_list = sorted(list(cfg.settings.get("ignored_dirs", [])))
        context.console.print(f"  - ignored_dirs: {ignored_list}")
        context.console.print(f"  - default_tree_depth: {cfg.settings.get('default_tree_depth')}")
        context.console.print(f"  - max_open_lines: {cfg.settings.get('max_open_lines')}")

        return CommandStatus.HANDLED
