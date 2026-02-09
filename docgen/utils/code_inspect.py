"""Lightweight code inspection for diagrams and summaries."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from ..config import DocGenConfig
from ..services.scan_service import _build_excludes
from ..utils.ignore import build_excluder
from ..utils.walk import walk_repo

MAX_FILE_BYTES = 200_000
MAX_CODE_FILES = 2000
MAX_CLASSES = 160
MAX_FUNCTIONS = 160
MAX_LISTED_FILES = 120
MAX_GRAPH_NODES = 50
MAX_GRAPH_EDGES = 160
MAX_MODULE_SUMMARIES = 80

PY_CLASS_RE = re.compile(r"^class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(([^)]*)\))?:")
PY_DEF_RE = re.compile(r"^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
JS_CLASS_RE = re.compile(r"^class\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s+extends\s+([A-Za-z0-9_.$]+))?")
PY_IMPORT_RE = re.compile(r"^\s*(?:from\s+([A-Za-z0-9_.]+)\s+import|import\s+([A-Za-z0-9_.]+))")
JS_IMPORT_RE = re.compile(r"""(?:from\s+['"](.+?)['"]|require\(\s*['"](.+?)['"]\s*\))""")


class CodeOverview:
    def __init__(self) -> None:
        self.code_files_by_ext: list[dict[str, Any]] = []
        self.python_classes: list[dict[str, Any]] = []
        self.python_edges: list[dict[str, str]] = []
        self.python_functions: list[dict[str, Any]] = []
        self.js_classes: list[dict[str, Any]] = []
        self.js_edges: list[dict[str, str]] = []
        self.ts_classes: list[dict[str, Any]] = []
        self.ts_edges: list[dict[str, str]] = []
        self.python_file_nodes: list[dict[str, str]] = []
        self.python_file_edges: list[dict[str, str]] = []
        self.js_file_nodes: list[dict[str, str]] = []
        self.js_file_edges: list[dict[str, str]] = []
        self.ts_file_nodes: list[dict[str, str]] = []
        self.ts_file_edges: list[dict[str, str]] = []
        self.python_module_summaries: list[dict[str, Any]] = []
        self.js_module_summaries: list[dict[str, Any]] = []
        self.ts_module_summaries: list[dict[str, Any]] = []
        self.code_entrypoints: list[str] = []
        self.code_files_sample: list[str] = []
        self.code_line_count: int = 0
        self.warnings: list[str] = []

    def to_context(self) -> dict[str, Any]:
        return {
            "code_files_by_ext": self.code_files_by_ext,
            "python_classes": self.python_classes,
            "python_edges": self.python_edges,
            "python_functions": self.python_functions,
            "js_classes": self.js_classes,
            "js_edges": self.js_edges,
            "ts_classes": self.ts_classes,
            "ts_edges": self.ts_edges,
            "python_file_nodes": self.python_file_nodes,
            "python_file_edges": self.python_file_edges,
            "js_file_nodes": self.js_file_nodes,
            "js_file_edges": self.js_file_edges,
            "ts_file_nodes": self.ts_file_nodes,
            "ts_file_edges": self.ts_file_edges,
            "python_module_summaries": self.python_module_summaries,
            "js_module_summaries": self.js_module_summaries,
            "ts_module_summaries": self.ts_module_summaries,
            "code_entrypoints": self.code_entrypoints,
            "code_files_sample": self.code_files_sample,
            "code_line_count": self.code_line_count,
            "code_warnings": self.warnings,
        }


def collect_code_overview(repo_path: Path, config: DocGenConfig) -> dict[str, Any]:
    overview = CodeOverview()

    patterns = _build_excludes(config.exclude, config.output_dir)
    excluder = build_excluder(patterns)
    files, _ = walk_repo(repo_path, excluder)

    rel_files = [path.as_posix() for path in files]
    if len(rel_files) > MAX_CODE_FILES:
        overview.warnings.append("Code scan truncated (too many files).")
        rel_files = rel_files[:MAX_CODE_FILES]

    code_files = [path for path in rel_files if _is_code_file(path)]
    overview.code_files_sample = code_files[:MAX_LISTED_FILES]

    ext_counts: dict[str, int] = {}
    total_lines = 0
    for path in code_files:
        ext = Path(path).suffix.lower() or "(none)"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
        content = _safe_read(repo_path / path)
        if content is not None:
            total_lines += len(content.splitlines())

    overview.code_line_count = total_lines

    overview.code_files_by_ext = [
        {"ext": ext, "count": count}
        for ext, count in sorted(ext_counts.items(), key=lambda item: (-item[1], item[0]))
    ]

    python_files = [path for path in code_files if path.endswith(".py")]
    js_files = [path for path in code_files if path.endswith(".js")]
    ts_files = [path for path in code_files if path.endswith(".ts") or path.endswith(".tsx")]

    overview.python_classes, overview.python_edges, overview.python_functions = _extract_python_symbols(
        repo_path, python_files
    )
    overview.js_classes, overview.js_edges = _extract_js_symbols(repo_path, js_files)
    overview.ts_classes, overview.ts_edges = _extract_js_symbols(repo_path, ts_files)

    overview.python_file_nodes, overview.python_file_edges = _python_import_graph(
        repo_path, python_files
    )
    overview.js_file_nodes, overview.js_file_edges = _js_import_graph(repo_path, js_files)
    overview.ts_file_nodes, overview.ts_file_edges = _js_import_graph(repo_path, ts_files)

    overview.python_module_summaries = _python_module_summaries(repo_path, python_files)
    overview.js_module_summaries = _js_module_summaries(repo_path, js_files)
    overview.ts_module_summaries = _js_module_summaries(repo_path, ts_files)
    overview.code_entrypoints = _detect_entrypoints(code_files)

    return overview.to_context()


def _is_code_file(path: str) -> bool:
    lowered = path.lower()
    return lowered.endswith((
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
    ))


def _extract_python_symbols(
    repo_path: Path,
    rel_paths: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[dict[str, Any]]]:
    classes: list[dict[str, Any]] = []
    functions: list[dict[str, Any]] = []

    for rel in rel_paths:
        if len(classes) >= MAX_CLASSES and len(functions) >= MAX_FUNCTIONS:
            break
        content = _safe_read(repo_path / rel)
        if content is None:
            continue

        for line in content.splitlines():
            if len(classes) < MAX_CLASSES:
                match = PY_CLASS_RE.match(line)
                if match:
                    name = match.group(1)
                    bases = _split_bases(match.group(2))
                    classes.append(_class_entry(rel, name, bases))
                    continue
            if len(functions) < MAX_FUNCTIONS:
                match = PY_DEF_RE.match(line)
                if match:
                    name = match.group(1)
                    functions.append({"name": name, "file": rel})

    classes = sorted(classes, key=lambda item: (item["file"], item["name"]))
    functions = sorted(functions, key=lambda item: (item["file"], item["name"]))

    edges = _build_edges(classes)
    return classes, edges, functions


def _extract_js_symbols(
    repo_path: Path,
    rel_paths: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    classes: list[dict[str, Any]] = []

    for rel in rel_paths:
        if len(classes) >= MAX_CLASSES:
            break
        content = _safe_read(repo_path / rel)
        if content is None:
            continue

        for line in content.splitlines():
            match = JS_CLASS_RE.match(line.strip())
            if not match:
                continue
            name = match.group(1)
            base = match.group(2)
            bases = [base] if base else []
            classes.append(_class_entry(rel, name, bases))

    classes = sorted(classes, key=lambda item: (item["file"], item["name"]))
    edges = _build_edges(classes)
    return classes, edges


def _safe_read(path: Path) -> str | None:
    try:
        if not path.is_file():
            return None
        if path.stat().st_size > MAX_FILE_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def _split_bases(raw: str | None) -> list[str]:
    if not raw:
        return []
    bases: list[str] = []
    for part in raw.split(","):
        cleaned = part.strip().split(" ")[0]
        if cleaned:
            bases.append(cleaned)
    return bases


def _class_entry(path: str, name: str, bases: list[str]) -> dict[str, Any]:
    class_id = _safe_id(f"{path}:{name}")
    return {
        "id": class_id,
        "name": name,
        "file": path,
        "bases": bases,
        "label": f"{name}\\n({path})",
    }


def _safe_id(value: str) -> str:
    safe = "".join(ch if ch.isalnum() else "_" for ch in value.lower())
    return safe or "node"


def _build_edges(classes: list[dict[str, Any]]) -> list[dict[str, str]]:
    name_to_id: dict[str, str] = {}
    for item in classes:
        if item["name"] not in name_to_id:
            name_to_id[item["name"]] = item["id"]

    edges: list[dict[str, str]] = []
    for item in classes:
        for base in item.get("bases", []):
            base_id = name_to_id.get(base)
            if base_id:
                edges.append({"from": base_id, "to": item["id"]})
    return edges


def _python_module_summaries(repo_path: Path, rel_paths: list[str]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for rel in rel_paths:
        if len(summaries) >= MAX_MODULE_SUMMARIES:
            break
        content = _safe_read(repo_path / rel)
        if content is None:
            continue
        classes = 0
        functions = 0
        for line in content.splitlines():
            if PY_CLASS_RE.match(line):
                classes += 1
            if PY_DEF_RE.match(line):
                functions += 1
        doc = _module_docstring(content)
        summaries.append(
            {
                "file": rel,
                "classes": classes,
                "functions": functions,
                "doc": doc,
            }
        )
    return sorted(summaries, key=lambda item: item["file"])


def _js_module_summaries(repo_path: Path, rel_paths: list[str]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for rel in rel_paths:
        if len(summaries) >= MAX_MODULE_SUMMARIES:
            break
        content = _safe_read(repo_path / rel)
        if content is None:
            continue
        classes = 0
        for line in content.splitlines():
            if JS_CLASS_RE.match(line.strip()):
                classes += 1
        summaries.append(
            {
                "file": rel,
                "classes": classes,
            }
        )
    return sorted(summaries, key=lambda item: item["file"])


def _module_docstring(content: str) -> str | None:
    stripped = content.lstrip()
    if stripped.startswith('"""') or stripped.startswith("'''"):
        quote = stripped[:3]
        rest = stripped[3:]
        end_idx = rest.find(quote)
        if end_idx != -1:
            doc = rest[:end_idx].strip().splitlines()
            if doc:
                return doc[0].strip()
    return None


def _detect_entrypoints(rel_paths: list[str]) -> list[str]:
    names = {
        "main.py",
        "app.py",
        "__main__.py",
        "manage.py",
        "server.py",
        "index.js",
        "index.ts",
        "index.tsx",
        "main.ts",
        "main.tsx",
    }
    entries = [path for path in rel_paths if path.split("/")[-1] in names]
    return sorted(entries)[:MAX_LISTED_FILES]


def _python_import_graph(
    repo_path: Path,
    rel_paths: list[str],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    module_map = _python_module_map(rel_paths)
    root_map = _python_root_map(module_map)

    edges: list[tuple[str, str]] = []
    for rel in rel_paths:
        content = _safe_read(repo_path / rel)
        if content is None:
            continue
        for line in content.splitlines():
            match = PY_IMPORT_RE.match(line)
            if not match:
                continue
            module = match.group(1) or match.group(2)
            if not module:
                continue
            target = module_map.get(module)
            if not target:
                root = module.split(".", 1)[0]
                target = root_map.get(root)
            if target:
                edges.append((rel, target))

    return _build_file_graph(rel_paths, edges)


def _js_import_graph(
    repo_path: Path,
    rel_paths: list[str],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    rel_set = set(rel_paths)
    edges: list[tuple[str, str]] = []

    for rel in rel_paths:
        content = _safe_read(repo_path / rel)
        if content is None:
            continue
        base_dir = Path(rel).parent
        for line in content.splitlines():
            match = JS_IMPORT_RE.search(line)
            if not match:
                continue
            raw = match.group(1) or match.group(2)
            if not raw or not raw.startswith("."):
                continue
            target = _resolve_js_import(base_dir, raw, rel_set)
            if target:
                edges.append((rel, target))

    return _build_file_graph(rel_paths, edges)


def _build_file_graph(
    rel_paths: list[str],
    edges: list[tuple[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    nodes: list[dict[str, str]] = []
    node_ids: dict[str, str] = {}

    for rel in rel_paths[:MAX_GRAPH_NODES]:
        node_id = _safe_id(rel)
        node_ids[rel] = node_id
        nodes.append({"id": node_id, "label": rel})

    filtered_edges: list[dict[str, str]] = []
    for source, target in edges:
        if source not in node_ids or target not in node_ids:
            continue
        filtered_edges.append({"from": node_ids[source], "to": node_ids[target]})
        if len(filtered_edges) >= MAX_GRAPH_EDGES:
            break

    return nodes, filtered_edges


def _python_module_map(rel_paths: list[str]) -> dict[str, str]:
    module_map: dict[str, str] = {}
    for rel in rel_paths:
        module = _python_module_name(rel)
        if module:
            module_map[module] = rel
    return module_map


def _python_root_map(module_map: dict[str, str]) -> dict[str, str]:
    roots: dict[str, str] = {}
    collisions: set[str] = set()
    for module, rel in module_map.items():
        root = module.split(".", 1)[0]
        if root in roots and roots[root] != rel:
            collisions.add(root)
        else:
            roots[root] = rel
    for root in collisions:
        roots.pop(root, None)
    return roots


def _python_module_name(rel: str) -> str | None:
    parts = rel.split('/')
    if not parts:
        return None
    if parts[0] in {'src', 'app', 'apps', 'packages', 'services', 'lib', 'libs'}:
        parts = parts[1:]
    if not parts:
        return None
    filename = parts[-1]
    if not filename.endswith('.py'):
        return None
    parts[-1] = filename[:-3]
    if parts[-1] == '__init__':
        parts = parts[:-1]
    if not parts:
        return None
    return '.'.join(parts)


def _resolve_js_import(base_dir: Path, raw: str, rel_set: set[str]) -> str | None:
    candidate = (base_dir / raw).as_posix()
    if candidate in rel_set:
        return candidate

    for ext in ('.ts', '.tsx', '.js', '.jsx'):
        with_ext = candidate + ext
        if with_ext in rel_set:
            return with_ext

    for ext in ('.ts', '.tsx', '.js', '.jsx'):
        index_path = f"{candidate}/index{ext}"
        if index_path in rel_set:
            return index_path

    return None
