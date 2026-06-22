class AccessControl:
    @staticmethod
    def get_behavior(mode: str) -> str:
        """Map permission mode key to behavior name."""
        if mode in ("1", "6"):
            return "Full Access"
        elif mode in ("2", "4"):
            return "Ask Before Edit"
        elif mode in ("3", "5"):
            return "Read Only"
        return "Read Only"  # Default fallback safe

    @classmethod
    def can_execute(cls, command_name: str, context, args: tuple = ()) -> bool:
        """Check if command can be executed under the current permission mode."""
        behavior = cls.get_behavior(context.current_permission)
        if behavior == "Read Only":
            context.console.print("Permission denied.")
            context.console.print("Current mode: Read Only")
            return False

        elif behavior == "Ask Before Edit":
            # Reconstruct the command string: <command_name> <args>
            arg_str = " ".join(args)
            full_cmd = f"{command_name} {arg_str}".strip()
            context.console.print("You are about to execute:")
            context.console.print(full_cmd)
            try:
                response = input("Proceed? (y/n) ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                return False
            if response in ("y", "yes"):
                return True
            return False

        elif behavior == "Full Access":
            return True

        return False
