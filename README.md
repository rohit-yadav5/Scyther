# Scyther

Scyther is a command-first, local-first developer CLI utility for repository inspection, navigation, and safe file mutations. It operates entirely locally and has no external AI dependencies, ensuring fast startup, deterministic behavior, and privacy.

---

## Core Capabilities

- **Repository Inspection & Navigation**: Search project files, view files with line numbers, display repository summaries, and list directories.
- **Symbol Analysis**: Locate definitions, usages, and internal dependencies of codebase symbols.
- **Safe File Operations**: Perform localized edits, directory creation, file creation, moving, and deletion safely under strict permission controls.
- **Git Integration**: View repository git status and diffs.

---

## Installation

### For Developers (From Source)

1. Clone the repository:
   ```bash
   git clone https://github.com/rohit-yadav5/Scyther.git
   cd Scyther
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt  # If any, or install 'tomli' for python < 3.11
   ```

3. Run Scyther:
   ```bash
   ./scyther
   ```

### From PyPI

Once published, you can install Scyther globally or in your active environment:
```bash
pip install scyther
```

---

## CLI Command Usage Examples

Start the interactive terminal by running `./scyther`. Inside the shell, you can run commands starting with `/`.

### Repository & Navigation Commands
- `/list` — List all files in the repository.
- `/tree [depth]` — Show directory tree up to the optional depth (defaults to configuration settings).
- `/find <filename>` — Find files matching a name.
- `/open <file>` — Open and view the content of a file.
- `/search <query>` — Search for text patterns inside files.
- `/summary` — View high-level repository summary.
- `/stats` — View language distribution and size metrics.
- `/recent [limit]` — List recently modified files.
- `/todo` — Scan codebase for tags like `TODO`, `FIXME`, `HACK`, `BUG`.

### Code Analysis Commands
- `/where <symbol>` — Find definitions of a symbol.
- `/refs <symbol>` — Find reference usages of a symbol.
- `/deps <path>` — View dependency map for a specific file.
- `/largest [limit]` — Display largest files in the repository.

### File Mutation Commands
- `/create <path>` — Create an empty file.
- `/mkdir <path>` — Create a directory.
- `/write <path> <content>` — Write content to a file (overwrites existing).
- `/append <path> <content>` — Append content to a file.
- `/replace <path> <old_text> <new_text>` — Search and replace text in a file.
- `/delete [--force] <path>` — Delete a file or directory.
- `/move <source> <destination>` — Move/rename files or folders.
- `/copy <source> <destination>` — Copy files or folders.

### System & Release Commands
- `/about` — Display package information.
- `/version` — Show current Scyther and Python versions.
- `/doctor` — Run diagnostic check rules to verify environment sanity.
- `/config` — Show loaded config files and active settings.
- `/permission` — Manage file access control mode.
- `/display` — Change terminal display mode.
- `/help [command]` — Display help information.
- `/exit` — Exit the interactive shell.

---

## Permission Subsystem

Scyther enforces strict project boundary checks. You cannot execute operations on paths that escape the project root directory, or on paths matching configured ignored directories (e.g. `.git`, `.venv`).

Additionally, mutation commands (such as `/write`, `/delete`, `/replace`, `/mkdir`) are regulated by three permission modes:
1. **Read-Only (1)**: All file changes and write operations are blocked.
2. **Ask Before Edit (2)**: Any mutation triggers a user confirmation prompt.
3. **Full Access (3)**: File mutations execute immediately without prompting.

Change your permission mode anytime using the `/permission` command.

---

## Configuration

Scyther loads settings from two optional TOML configuration files, merging them (project-level settings override user-level defaults):
1. **Project Config**: `.scyther.toml` in the project root.
2. **Global Config**: `~/.scyther/config.toml` in your home folder.

### Supported Options
```toml
# Example .scyther.toml
ignored_dirs = [
    ".git",
    ".venv",
    ".cache",
    ".pytest_cache",
    "__pycache__",
    "node_modules"
]
default_tree_depth = 3
max_open_lines = 500
```

---

## Running Tests

Run the full automated test suite using `pytest`:
```bash
source .venv/bin/activate
PYTHONPATH=. pytest tests/ -v
```