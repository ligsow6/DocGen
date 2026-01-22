"""Stub scan service for DocGen."""

from pathlib import Path

from ..config import DocGenConfig
from ..models import Commands, DetectedFile, DocsInfo, ProjectInfo


def scan_repo(repo_path: Path, config: DocGenConfig) -> ProjectInfo:
    output_dir = config.output_dir.rstrip("/")
    docs = DocsInfo(
        readme_path=f"{output_dir}/README.md",
        architecture_path=f"{output_dir}/ARCHITECTURE.md",
        github_pages_dir=f"{output_dir}/",
        doxygen_dir=f"{output_dir}/doxygen/",
    )

    files_detected = [
        DetectedFile(path="pyproject.toml", type="python"),
        DetectedFile(path="requirements.txt", type="python"),
        DetectedFile(path="package.json", type="node"),
        DetectedFile(path="Dockerfile", type="docker"),
        DetectedFile(path=".github/workflows/ci.yml", type="github_actions"),
    ]

    commands = Commands(
        run="python -m docgen",
        test="pytest",
        lint="ruff check .",
        format="ruff format .",
    )

    return ProjectInfo(
        project_name=repo_path.name,
        repo_root=str(repo_path),
        stacks=["python", "node", "docker"],
        files_detected=files_detected,
        commands=commands,
        ci=["github_actions"],
        docs=docs,
    )
