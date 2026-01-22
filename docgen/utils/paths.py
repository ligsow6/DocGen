"""Path helpers."""

from pathlib import Path

from ..errors import DocGenIOError


def resolve_repo_path(repo_path: Path | None) -> Path:
    path = repo_path or Path.cwd()
    path = path.expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise DocGenIOError(f"Repository path not found: {path}")
    return path
