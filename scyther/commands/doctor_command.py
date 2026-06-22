import os
import subprocess
import shutil
from scyther.core.models import CommandStatus


class DoctorCommand:
    """/doctor — run diagnostics to check environment status."""

    @staticmethod
    def execute(args: tuple, context) -> CommandStatus:
        repo_path = str(context.project_root)
        context.console.print(f"Active Repository: {repo_path}")

        read_ok = os.access(repo_path, os.R_OK)
        context.console.print(f"Read access: {'OK' if read_ok else 'Failed'}")

        write_ok = os.access(repo_path, os.W_OK)
        context.console.print(f"Write access: {'OK' if write_ok else 'Failed'}")

        git_path = shutil.which("git")
        if git_path:
            try:
                res = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True)
                # Parse "git version X.Y.Z"
                git_version = res.stdout.strip()
                if git_version.startswith("git version "):
                    git_version = git_version[12:]
                context.console.print(f"Git Binary: Available (version {git_version})")
            except Exception:
                context.console.print("Git Binary: Available (failed to get version)")
        else:
            context.console.print("Git Binary: Not available")

        return CommandStatus.HANDLED
