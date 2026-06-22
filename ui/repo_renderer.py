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

    @staticmethod
    def render_largest(largest_files: list[dict], context) -> None:
        if not largest_files:
            context.console.print("No files found in repository.")
            return

        def format_size(size_in_bytes: int) -> str:
            if size_in_bytes >= 1024 * 1024:
                return f"{size_in_bytes / (1024 * 1024):.1f} MB"
            elif size_in_bytes >= 1024:
                return f"{size_in_bytes / 1024:.1f} KB"
            else:
                return f"{size_in_bytes} B"

        for idx, item in enumerate(largest_files, 1):
            path = item["path"]
            size_str = format_size(item["size"])
            context.console.print(f"{idx}. {path:<40} {size_str:>8}")
