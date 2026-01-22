"""Stub build service for DocGen."""

from pathlib import Path

from ..config import DocGenConfig


def build_docs(repo_path: Path, config: DocGenConfig, dry_run: bool = False) -> list[Path]:
    output_dir = (repo_path / config.output_dir).resolve()
    targets = [output_dir / "README.md", output_dir / "ARCHITECTURE.md"]

    if dry_run:
        return targets

    output_dir.mkdir(parents=True, exist_ok=True)

    for target in targets:
        if target.exists():
            continue
        target.write_text(_stub_content(target.name, repo_path.name), encoding="utf-8")

    return targets


def _stub_content(filename: str, project_name: str) -> str:
    if filename.lower() == "readme.md":
        return (
            f"# {project_name}\n\n"
            "DocGen build stub. Content will be generated in a later step.\n"
        )
    return (
        "# Architecture\n\n"
        "DocGen build stub. Content will be generated in a later step.\n"
    )
