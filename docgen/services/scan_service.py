"""Filesystem scan service for DocGen."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import tomllib

from ..config import DocGenConfig
from ..errors import DocGenIOError
from ..models import Commands, DetectedFile, DocsInfo, ProjectInfo, StackInfo
from ..utils.ignore import build_excluder
from ..utils.walk import walk_repo

COMPOSE_FILES = {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}
NODE_LOCKFILES = ["pnpm-lock.yaml", "yarn.lock", "package-lock.json"]


def scan_repo(repo_path: Path, config: DocGenConfig) -> ProjectInfo:
    output_dir = _normalize_output_dir(config.output_dir)
    docs = DocsInfo(
        readme_path=f"{output_dir}/README.md",
        architecture_path=f"{output_dir}/ARCHITECTURE.md",
        github_pages_dir=f"{output_dir}/" if output_dir != "." else "./",
        doxygen_dir=f"{output_dir}/api/" if output_dir != "." else "./api/",
    )

    patterns = _build_excludes(config.exclude, output_dir)
    excluder = build_excluder(patterns)

    try:
        files, _ = walk_repo(repo_path, excluder)
    except OSError as exc:
        raise DocGenIOError(str(exc)) from exc

    rel_files = sorted(path.as_posix() for path in files)
    files_detected, ci = _detect_key_files(repo_path, rel_files, output_dir)

    warnings: list[str] = []
    package_manager, node_scripts = _read_node_scripts(repo_path, rel_files, warnings)
    python_info = _read_python_info(repo_path, rel_files, warnings)
    docker_info = _read_docker_info(rel_files)

    stacks = _build_stacks(rel_files, package_manager, python_info, docker_info)
    commands = _build_commands(
        repo_path=repo_path,
        node_scripts=node_scripts,
        package_manager=package_manager,
        python_info=python_info,
        docker_info=docker_info,
    )

    if not rel_files:
        warnings.append("Repository appears empty or fully excluded.")
    if not stacks:
        warnings.append("No stack detected.")

    return ProjectInfo(
        project_name=repo_path.name,
        repo_root=repo_path.as_posix(),
        stacks=sorted(stacks, key=lambda item: item.name),
        files_detected=sorted(files_detected, key=lambda item: (item.path, item.type)),
        commands=commands,
        ci=sorted(ci),
        docs=docs,
        package_manager=package_manager,
        python_tooling=python_info.tool,
        warnings=sorted(set(warnings)),
    )


def _normalize_output_dir(output_dir: str) -> str:
    normalized = output_dir.strip().replace("\\", "/")
    if not normalized:
        return "DocGen"
    return normalized.rstrip("/")


def _build_excludes(excludes: list[str], output_dir: str) -> list[str]:
    patterns = list(excludes)
    if not _has_pattern(patterns, ".git/"):
        patterns.append(".git/")
    if output_dir not in {".", "./", ""}:
        output_pattern = output_dir.rstrip("/") + "/"
        if not _has_pattern(patterns, output_pattern):
            patterns.append(output_pattern)
    return patterns


def _has_pattern(patterns: list[str], pattern: str) -> bool:
    normalized = pattern.strip().replace("\\", "/")
    for item in patterns:
        if item.strip().replace("\\", "/") == normalized:
            return True
    return False


def _detect_key_files(
    repo_path: Path,
    rel_files: list[str],
    output_dir: str,
) -> tuple[list[DetectedFile], set[str]]:
    detected: list[DetectedFile] = []
    ci: set[str] = set()

    rel_file_set = set(rel_files)

    def add(paths: list[str], dtype: str) -> None:
        for path in paths:
            detected.append(DetectedFile(path=path, type=dtype))

    by_name = _index_by_name(rel_files)

    add(by_name.get("package.json", []), "node")
    add(by_name.get("package-lock.json", []), "node_lock_npm")
    add(by_name.get("yarn.lock", []), "node_lock_yarn")
    add(by_name.get("pnpm-lock.yaml", []), "node_lock_pnpm")
    add(by_name.get("tsconfig.json", []), "typescript")

    add(by_name.get("pyproject.toml", []), "python")
    add(by_name.get("requirements.txt", []), "python")
    add(by_name.get("setup.cfg", []), "python")
    add(by_name.get("Pipfile", []), "python")
    add(by_name.get("poetry.lock", []), "python")

    add(by_name.get("Dockerfile", []), "docker")
    for compose_name in COMPOSE_FILES:
        add(by_name.get(compose_name, []), "docker_compose")

    add(by_name.get("Doxyfile", []), "doxygen")

    add(by_name.get("Jenkinsfile", []), "jenkins")
    if by_name.get("Jenkinsfile"):
        ci.add("jenkins")

    add(by_name.get(".gitlab-ci.yml", []), "gitlab_ci")
    if by_name.get(".gitlab-ci.yml"):
        ci.add("gitlab_ci")

    github_actions = [
        path
        for path in rel_files
        if path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml"))
    ]
    if github_actions:
        add(github_actions, "github_actions")
        ci.add("github_actions")

    readmes = [path for path in rel_files if path.endswith("/README.md") or path == "README.md"]
    add(readmes, "readme")

    normalized_output = output_dir.strip().replace("\\", "/").rstrip("/")
    if normalized_output and normalized_output not in {".", "./"}:
        docs_dir = repo_path / normalized_output
        if docs_dir.is_dir():
            detected.append(DetectedFile(path=f"{normalized_output}/", type="docs_dir"))

    if normalized_output != "docs":
        docs_dir = repo_path / "docs"
        if docs_dir.is_dir():
            detected.append(DetectedFile(path="docs/", type="docs_dir"))

    if "README.md" not in rel_file_set and (repo_path / "README.md").is_file():
        detected.append(DetectedFile(path="README.md", type="readme"))

    return detected, ci


def _index_by_name(rel_files: list[str]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for path in rel_files:
        name = path.rsplit("/", 1)[-1]
        index.setdefault(name, []).append(path)
    for value in index.values():
        value.sort()
    return index


def _read_node_scripts(
    repo_path: Path,
    rel_files: list[str],
    warnings: list[str],
) -> tuple[str | None, dict[str, str]]:
    by_name = _index_by_name(rel_files)
    package_json_paths = by_name.get("package.json", [])
    if not package_json_paths:
        return None, {}

    package_json_path = _select_primary(package_json_paths)
    package_manager = _detect_package_manager(by_name)

    payload = _read_json(repo_path / package_json_path, warnings)
    if not isinstance(payload, dict):
        return package_manager, {}

    scripts = payload.get("scripts")
    if not isinstance(scripts, dict):
        return package_manager, {}

    return package_manager, {str(key): str(value) for key, value in scripts.items() if isinstance(key, str)}


def _detect_package_manager(by_name: dict[str, list[str]]) -> str:
    if by_name.get("pnpm-lock.yaml"):
        return "pnpm"
    if by_name.get("yarn.lock"):
        return "yarn"
    return "npm"


def _read_python_info(
    repo_path: Path,
    rel_files: list[str],
    warnings: list[str],
) -> "PythonInfo":
    by_name = _index_by_name(rel_files)
    pyproject_paths = by_name.get("pyproject.toml", [])
    requirements_paths = by_name.get("requirements.txt", [])
    poetry_lock_present = bool(by_name.get("poetry.lock"))
    has_python_signals = bool(
        pyproject_paths
        or requirements_paths
        or by_name.get("setup.cfg")
        or by_name.get("Pipfile")
        or poetry_lock_present
    )

    pyproject_data: dict[str, Any] = {}
    if pyproject_paths:
        pyproject_path = _select_primary(pyproject_paths)
        pyproject_data = _read_toml(repo_path / pyproject_path, warnings)

    requirements_lines: list[str] = []
    if requirements_paths:
        requirements_path = _select_primary(requirements_paths)
        requirements_lines = _read_requirements(repo_path / requirements_path, warnings)

    return _analyze_python(
        pyproject_data,
        requirements_lines,
        poetry_lock_present,
        rel_files,
        has_python_signals,
    )


class PythonInfo:
    def __init__(
        self,
        tool: str | None,
        has_pytest: bool,
        has_ruff: bool,
        has_black: bool,
        has_flake8: bool,
        has_python: bool,
    ):
        self.tool = tool
        self.has_pytest = has_pytest
        self.has_ruff = has_ruff
        self.has_black = has_black
        self.has_flake8 = has_flake8
        self.has_python = has_python


class DockerInfo:
    def __init__(self, has_dockerfile: bool, has_compose: bool):
        self.has_dockerfile = has_dockerfile
        self.has_compose = has_compose


def _read_docker_info(rel_files: list[str]) -> DockerInfo:
    by_name = _index_by_name(rel_files)
    has_dockerfile = bool(by_name.get("Dockerfile"))
    has_compose = any(by_name.get(name) for name in COMPOSE_FILES)
    return DockerInfo(has_dockerfile=has_dockerfile, has_compose=has_compose)


def _analyze_python(
    pyproject_data: dict[str, Any],
    requirements_lines: list[str],
    poetry_lock_present: bool,
    rel_files: list[str],
    has_python_signals: bool,
) -> PythonInfo:
    tool_section = pyproject_data.get("tool") if isinstance(pyproject_data, dict) else {}
    tool_section = tool_section if isinstance(tool_section, dict) else {}

    has_pytest_section = "pytest" in tool_section
    has_ruff_section = "ruff" in tool_section
    has_black_section = "black" in tool_section
    has_flake8_section = "flake8" in tool_section

    deps = _collect_pyproject_deps(pyproject_data)

    requirements_text = "\n".join(requirements_lines).lower()

    def dep_contains(name: str) -> bool:
        lowered = name.lower()
        return any(lowered in dep for dep in deps) or lowered in requirements_text

    has_pytest = has_pytest_section or dep_contains("pytest")
    has_ruff = has_ruff_section or dep_contains("ruff")
    has_black = has_black_section or dep_contains("black")
    has_flake8 = has_flake8_section or dep_contains("flake8")

    has_tests_dir = any(path.startswith("tests/") for path in rel_files)
    if has_tests_dir and not has_pytest:
        has_pytest = True

    tool = None
    if "poetry" in tool_section or poetry_lock_present:
        tool = "poetry"

    return PythonInfo(tool, has_pytest, has_ruff, has_black, has_flake8, has_python_signals)


def _collect_pyproject_deps(pyproject_data: dict[str, Any]) -> list[str]:
    deps: list[str] = []
    if not isinstance(pyproject_data, dict):
        return deps
    project_section = pyproject_data.get("project")
    if isinstance(project_section, dict):
        project_deps = project_section.get("dependencies", [])
        if isinstance(project_deps, list):
            deps.extend([str(item).lower() for item in project_deps])
        optional_deps = project_section.get("optional-dependencies", {})
        if isinstance(optional_deps, dict):
            for values in optional_deps.values():
                if isinstance(values, list):
                    deps.extend([str(item).lower() for item in values])
    return deps


def _build_stacks(
    rel_files: list[str],
    package_manager: str | None,
    python_info: PythonInfo,
    docker_info: DockerInfo,
) -> list[StackInfo]:
    by_name = _index_by_name(rel_files)
    stacks: list[StackInfo] = []

    node_evidence = _collect_evidence(by_name, ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "tsconfig.json"])
    if node_evidence:
        confidence = 1.0 if by_name.get("package.json") else 0.6
        attributes: dict[str, Any] = {}
        if by_name.get("tsconfig.json"):
            attributes["typescript"] = True
        if package_manager:
            attributes["package_manager"] = package_manager
        stacks.append(StackInfo(name="node", confidence=confidence, evidence=node_evidence, attributes=attributes))

    python_evidence = _collect_evidence(by_name, ["pyproject.toml", "requirements.txt", "setup.cfg", "Pipfile", "poetry.lock"])
    if python_evidence:
        confidence = 1.0 if (by_name.get("pyproject.toml") or by_name.get("requirements.txt")) else 0.6
        attributes = {}
        if python_info.tool:
            attributes["tool"] = python_info.tool
        stacks.append(StackInfo(name="python", confidence=confidence, evidence=python_evidence, attributes=attributes))

    docker_evidence = _collect_evidence(by_name, ["Dockerfile", *sorted(COMPOSE_FILES)])
    if docker_evidence:
        confidence = 0.9
        attributes = {}
        if docker_info.has_compose:
            attributes["compose"] = True
        stacks.append(StackInfo(name="docker", confidence=confidence, evidence=docker_evidence, attributes=attributes))

    return stacks


def _collect_evidence(by_name: dict[str, list[str]], names: list[str]) -> list[str]:
    evidence: list[str] = []
    for name in names:
        evidence.extend(by_name.get(name, []))
    return sorted(set(evidence))


def _build_commands(
    repo_path: Path,
    node_scripts: dict[str, str],
    package_manager: str | None,
    python_info: PythonInfo,
    docker_info: DockerInfo,
) -> Commands:
    commands = Commands()

    node_commands = _node_commands(node_scripts, package_manager)
    commands = _merge_commands(commands, node_commands)

    python_commands = _python_commands(python_info)
    commands = _merge_commands(commands, python_commands)

    docker_commands = _docker_commands(repo_path, docker_info)
    commands = _merge_commands(commands, docker_commands)

    return commands


def _node_commands(scripts: dict[str, str], package_manager: str | None) -> Commands:
    if not scripts:
        return Commands()

    pm = package_manager or "npm"

    def cmd(script: str) -> str:
        if pm == "yarn":
            return f"yarn {script}"
        if pm == "pnpm":
            return f"pnpm {script}"
        return f"npm run {script}"

    run_script = "dev" if "dev" in scripts else "start" if "start" in scripts else None
    test_script = "test" if "test" in scripts else None
    lint_script = "lint" if "lint" in scripts else None
    build_script = "build" if "build" in scripts else None

    return Commands(
        run=cmd(run_script) if run_script else None,
        test=cmd(test_script) if test_script else None,
        lint=cmd(lint_script) if lint_script else None,
        build=cmd(build_script) if build_script else None,
    )


def _python_commands(info: PythonInfo) -> Commands:
    if not info.has_python:
        return Commands()
    prefix = "poetry run " if info.tool == "poetry" else ""

    test_cmd = f"{prefix}pytest" if info.has_pytest else None

    lint_cmd = None
    if info.has_ruff:
        lint_cmd = f"{prefix}ruff check ."
    elif info.has_flake8:
        lint_cmd = f"{prefix}flake8"
    elif info.has_black:
        lint_cmd = f"{prefix}black --check ."

    return Commands(
        test=test_cmd,
        lint=lint_cmd,
    )


def _docker_commands(repo_path: Path, info: DockerInfo) -> Commands:
    if info.has_compose:
        return Commands(run="docker compose up --build", build="docker compose build")
    if info.has_dockerfile:
        return Commands(build=f"docker build -t {repo_path.name}:latest .")
    return Commands()


def _merge_commands(base: Commands, incoming: Commands) -> Commands:
    return Commands(
        run=base.run or incoming.run,
        test=base.test or incoming.test,
        lint=base.lint or incoming.lint,
        build=base.build or incoming.build,
        format=base.format or incoming.format,
    )


def _select_primary(paths: list[str]) -> str:
    return sorted(paths, key=lambda item: (item.count("/"), item))[0]


def _read_json(path: Path, warnings: list[str]) -> dict[str, Any] | None:
    try:
        content = path.read_text(encoding="utf-8")
        return json.loads(content)
    except (OSError, json.JSONDecodeError) as exc:
        warnings.append(f"Failed to parse JSON: {path}: {exc}")
        return None


def _read_toml(path: Path, warnings: list[str]) -> dict[str, Any]:
    try:
        content = path.read_text(encoding="utf-8")
        return tomllib.loads(content)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        warnings.append(f"Failed to parse TOML: {path}: {exc}")
        return {}


def _read_requirements(path: Path, warnings: list[str]) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        warnings.append(f"Failed to read requirements: {path}: {exc}")
        return []

    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        cleaned.append(stripped)
    return cleaned
