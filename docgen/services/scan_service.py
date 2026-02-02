"""Filesystem scan service for DocGen."""

from __future__ import annotations

from pathlib import Path

from ..config import DocGenConfig
from ..errors import DocGenIOError
from ..models import Commands, DetectedFile, DocsInfo, ProjectInfo
from ..utils.ignore import build_excluder
from ..utils.walk import walk_repo


def scan_repo(repo_path: Path, config: DocGenConfig) -> ProjectInfo:
    output_dir = _normalize_output_dir(config.output_dir)
    docs = DocsInfo(
        readme_path=f"{output_dir}/README.md",
        architecture_path=f"{output_dir}/ARCHITECTURE.md",
        github_pages_dir=f"{output_dir}/" if output_dir != "." else "./",
        doxygen_dir=f"{output_dir}/doxygen/" if output_dir != "." else "./doxygen/",
    )

    patterns = _build_excludes(config.exclude, output_dir)
    excluder = build_excluder(patterns)

    try:
        files, _ = walk_repo(repo_path, excluder)
    except OSError as exc:
        raise DocGenIOError(str(exc)) from exc
    rel_files = sorted(path.as_posix() for path in files)

    files_detected, stacks, ci = _detect_key_files(
        repo_path=repo_path,
        rel_files=rel_files,
    )

    return ProjectInfo(
        project_name=repo_path.name,
        repo_root=repo_path.as_posix(),
        stacks=sorted(stacks),
        files_detected=sorted(files_detected, key=lambda item: (item.path, item.type)),
        commands=Commands(),
        ci=sorted(ci),
        docs=docs,
    )


def _normalize_output_dir(output_dir: str) -> str:
    normalized = output_dir.strip().replace("\\", "/")
    if not normalized:
        return "docs"
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
) -> tuple[list[DetectedFile], set[str], set[str]]:
    detected: list[DetectedFile] = []
    stacks: set[str] = set()
    ci: set[str] = set()

    rel_file_set = set(rel_files)

    def add(path: str, dtype: str) -> None:
        detected.append(DetectedFile(path=path, type=dtype))

    for rel_path in rel_files:
        name = rel_path.split("/")[-1]

        if name == "package.json":
            stacks.add("node")
            add(rel_path, "node")
            continue
        if name == "package-lock.json":
            stacks.add("node")
            add(rel_path, "node_lock_npm")
            continue
        if name == "yarn.lock":
            stacks.add("node")
            add(rel_path, "node_lock_yarn")
            continue
        if name == "pnpm-lock.yaml":
            stacks.add("node")
            add(rel_path, "node_lock_pnpm")
            continue
        if name == "tsconfig.json":
            stacks.add("node")
            add(rel_path, "typescript")
            continue

        if name == "pyproject.toml":
            stacks.add("python")
            add(rel_path, "python")
            continue
        if name == "requirements.txt":
            stacks.add("python")
            add(rel_path, "python")
            continue
        if name == "setup.cfg":
            stacks.add("python")
            add(rel_path, "python")
            continue
        if name == "Pipfile":
            stacks.add("python")
            add(rel_path, "python")
            continue
        if name == "poetry.lock":
            stacks.add("python")
            add(rel_path, "python")
            continue

        if name == "Dockerfile":
            stacks.add("docker")
            add(rel_path, "docker")
            continue
        if name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}:
            stacks.add("docker")
            add(rel_path, "docker_compose")
            continue

        if name == "Doxyfile":
            add(rel_path, "doxygen")
            continue

        if name == "Jenkinsfile":
            ci.add("jenkins")
            add(rel_path, "jenkins")
            continue

        if name == ".gitlab-ci.yml":
            ci.add("gitlab_ci")
            add(rel_path, "gitlab_ci")
            continue

        if rel_path.startswith(".github/workflows/") and name.endswith((".yml", ".yaml")):
            ci.add("github_actions")
            add(rel_path, "github_actions")
            continue

        if rel_path == "README.md":
            add(rel_path, "readme")

    docs_dir = repo_path / "docs"
    if docs_dir.is_dir():
        add("docs/", "docs_dir")

    if "README.md" not in rel_file_set and (repo_path / "README.md").is_file():
        add("README.md", "readme")

    return detected, stacks, ci
