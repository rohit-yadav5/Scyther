from rich.console import Console

console = Console()


class RepoRenderer:
    @staticmethod
    def render_file_list(files):
        console.print(f"Files ({len(files)})")
        grouped = {}
        for file_path in files:
            parts = file_path.split("/")
            if len(parts) == 1:
                grouped.setdefault(".", []).append(parts[0])
            else:
                grouped.setdefault("/".join(parts[:-1]), []).append(parts[-1])

        for directory in sorted(grouped.keys()):
            if directory != ".":
                console.print()
                console.print(f"{directory}/")
            for filename in sorted(grouped[directory]):
                prefix = "  " if directory != "." else ""
                console.print(f"{prefix}{filename}")

    @staticmethod
    def render_tree(tree):
        console.print(".")

        def render_node(children, prefix=""):
            for index, child in enumerate(children):
                is_last = index == len(children) - 1
                branch = "└── " if is_last else "├── "
                suffix = "" if child["type"] == "file" else "/"
                console.print(f"{prefix}{branch}{child['name']}{suffix}")
                next_prefix = f"{prefix}    " if is_last else f"{prefix}│   "
                render_node(child["children"], next_prefix)

        render_node(tree["tree"]["children"])

    @staticmethod
    def render_summary(summary):
        console.print(f"Repository Root: {summary['root']}")
        console.print(f"Files: {summary['files']}")
        console.print(f"Directories: {summary['directories']}")
