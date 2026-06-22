import re
from pathlib import Path

from scyther.core.models import SymbolLocation, FileDependency
from scyther.tools.repo_tool import RepoTool


class CodeIndexService:
    SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx"}

    def __init__(self, project_root: str, config=None):
        self.project_root = Path(project_root).resolve()
        self.config = config

    @property
    def ignored_dirs(self):
        return self.config.ignored_dirs if self.config else None

    def find_definitions(self, symbol: str) -> list[SymbolLocation]:
        """Find definitions of the given symbol in the project root."""
        definitions = []
        symbol_pattern = symbol.strip()
        if not symbol_pattern:
            return []

        py_class_re = re.compile(r'^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)')
        py_def_re = re.compile(r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)')
        js_def_re = re.compile(r'^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?(class|function|interface|type)\s+([a-zA-Z_][a-zA-Z0-9_]*)')
        js_arrow_re = re.compile(r'^\s*(?:export\s+)?(?:const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?:\([^)]*\)|[a-zA-Z_][a-zA-Z0-9_]*|\s*)\s*=>')

        for root, path in RepoTool._walk(str(self.project_root), ignored_dirs=self.ignored_dirs):
            if not path.is_file():
                continue
            suffix = path.suffix.lower()
            if suffix not in self.SUPPORTED_EXTENSIONS:
                continue

            rel_path = path.relative_to(root).as_posix()
            try:
                lines = path.read_text(errors='ignore').splitlines()
            except Exception:
                continue

            for idx, line in enumerate(lines, 1):
                name = None
                if suffix == ".py":
                    m = py_class_re.match(line)
                    if m:
                        name = m.group(1)
                    else:
                        m = py_def_re.match(line)
                        if m:
                            name = m.group(1)
                elif suffix in (".js", ".ts", ".jsx", ".tsx"):
                    m = js_def_re.match(line)
                    if m:
                        name = m.group(2)
                    else:
                        m = js_arrow_re.match(line)
                        if m:
                            name = m.group(1)

                if name == symbol_pattern:
                    definitions.append(SymbolLocation(path=rel_path, line=idx, symbol=name))

        return definitions

    def find_references(self, symbol: str) -> list[SymbolLocation]:
        """Find occurrences/references of the given symbol in the project root."""
        symbol_pattern = symbol.strip()
        if not symbol_pattern:
            return []

        definitions = self.find_definitions(symbol_pattern)
        def_locations = {(d.path, d.line) for d in definitions}

        references = []
        pattern = re.compile(rf'\b{re.escape(symbol_pattern)}\b')

        for root, path in RepoTool._walk(str(self.project_root), ignored_dirs=self.ignored_dirs):
            if not path.is_file():
                continue
            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            rel_path = path.relative_to(root).as_posix()
            try:
                content = path.read_text(errors='ignore')
            except Exception:
                continue

            lines = content.splitlines()
            for idx, line in enumerate(lines, 1):
                if (rel_path, idx) in def_locations:
                    continue
                if pattern.search(line):
                    references.append(SymbolLocation(path=rel_path, line=idx, symbol=symbol_pattern))

        return references

    def get_dependencies(self, file_path_str: str) -> list[FileDependency]:
        """Find direct internal dependencies of the file."""
        target_path = None
        from scyther.services.file_service import FileService
        file_service = FileService(str(self.project_root))
        try:
            resolved_abs_path = file_service.resolve_path(file_path_str)
            target_path = Path(resolved_abs_path)
        except Exception:
            matches = RepoTool.find_file(str(self.project_root), file_path_str, ignored_dirs=self.ignored_dirs)
            if not matches:
                p = self.project_root / file_path_str
                if p.is_file():
                    target_path = p.resolve()
            else:
                target_path = (self.project_root / matches[0]).resolve()

        if not target_path or not target_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path_str}")

        suffix = target_path.suffix.lower()
        if suffix not in self.SUPPORTED_EXTENSIONS:
            return []

        rel_source = target_path.relative_to(self.project_root).as_posix()
        try:
            content = target_path.read_text(errors='ignore')
        except Exception:
            return []

        imported_modules = []

        if suffix == ".py":
            import_re = re.compile(r'^\s*import\s+([^#\n]+)')
            from_import_re = re.compile(r'^\s*from\s+(\S+)\s+import\s+([^#\n]+)')
            for line in content.splitlines():
                m = from_import_re.match(line)
                if m:
                    imported_modules.append(m.group(1))
                    continue
                m = import_re.match(line)
                if m:
                    parts = m.group(1).split(',')
                    for part in parts:
                        name = part.split('as')[0].strip()
                        if name:
                            imported_modules.append(name)
            
            dependencies = []
            for mod in imported_modules:
                resolved = self._resolve_python_import(target_path, mod)
                if resolved:
                    rel_target = resolved.relative_to(self.project_root).as_posix()
                    if rel_target != rel_source:
                        dependencies.append(FileDependency(source=rel_source, target=rel_target))
            return dependencies

        elif suffix in (".js", ".ts", ".jsx", ".tsx"):
            js_import_re = re.compile(r'(?:import|export)\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]')
            js_require_re = re.compile(r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)')
            
            imported_paths = js_import_re.findall(content)
            imported_paths.extend(js_require_re.findall(content))

            dependencies = []
            for imp in imported_paths:
                resolved = self._resolve_js_import(target_path, imp)
                if resolved:
                    rel_target = resolved.relative_to(self.project_root).as_posix()
                    if rel_target != rel_source:
                        dependencies.append(FileDependency(source=rel_source, target=rel_target))
            return dependencies

        return []

    def _resolve_python_import(self, importing_file: Path, module_name: str) -> Path | None:
        if module_name.startswith('.'):
            dots_count = 0
            for char in module_name:
                if char == '.':
                    dots_count += 1
                else:
                    break
            rem = module_name[dots_count:]
            base_dir = importing_file.parent
            for _ in range(dots_count - 1):
                base_dir = base_dir.parent
            if rem:
                path_str = rem.replace('.', '/')
                candidates = [
                    base_dir / f"{path_str}.py",
                    base_dir / path_str / "__init__.py"
                ]
            else:
                candidates = [
                    base_dir / "__init__.py"
                ]
        else:
            path_str = module_name.replace('.', '/')
            candidates = [
                self.project_root / f"{path_str}.py",
                self.project_root / path_str / "__init__.py",
                importing_file.parent / f"{path_str}.py",
                importing_file.parent / path_str / "__init__.py"
            ]

        for cand in candidates:
            try:
                res = cand.resolve()
                if res.is_file() and res.relative_to(self.project_root):
                    return res
            except (ValueError, OSError):
                continue
        return None

    def _resolve_js_import(self, importing_file: Path, import_path: str) -> Path | None:
        if not (import_path.startswith('./') or import_path.startswith('../')):
            candidates = [
                self.project_root / import_path,
                importing_file.parent / import_path
            ]
        else:
            candidates = [
                importing_file.parent / import_path
            ]

        for cand in candidates:
            for ext in ["", ".js", ".ts", ".jsx", ".tsx", ".d.ts"]:
                test_path = cand.with_name(cand.name + ext) if ext else cand
                try:
                    res = test_path.resolve()
                    if res.is_file() and res.relative_to(self.project_root):
                        return res
                except (ValueError, OSError):
                    pass
            for ext in [".js", ".ts", ".jsx", ".tsx"]:
                test_path = cand / f"index{ext}"
                try:
                    res = test_path.resolve()
                    if res.is_file() and res.relative_to(self.project_root):
                        return res
                except (ValueError, OSError):
                    pass
        return None
