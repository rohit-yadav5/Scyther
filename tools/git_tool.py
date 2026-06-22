import subprocess


class GitTool:
    @staticmethod
    def run_git(cwd: str, args: list[str]) -> subprocess.CompletedProcess:
        """Run a git command in the specified working directory."""
        try:
            return subprocess.run(
                ["git"] + args,
                cwd=cwd,
                capture_output=True,
                text=True
            )
        except FileNotFoundError:
            raise RuntimeError("Git command not found. Please ensure Git is installed.")

    @staticmethod
    def git_status(cwd: str) -> str:
        res = GitTool.run_git(cwd, ["status", "--short"])
        if res.returncode != 0:
            raise RuntimeError(res.stderr.strip() or f"git status failed with exit code {res.returncode}")
        return res.stdout

    @staticmethod
    def git_diff(cwd: str) -> str:
        res = GitTool.run_git(cwd, ["diff"])
        if res.returncode != 0:
            raise RuntimeError(res.stderr.strip() or f"git diff failed with exit code {res.returncode}")
        return res.stdout

    @staticmethod
    def is_git_repository(cwd: str) -> bool:
        res = GitTool.run_git(cwd, ["rev-parse", "--is-inside-work-tree"])
        return res.returncode == 0
