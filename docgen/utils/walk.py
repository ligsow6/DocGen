"""Repository walker with exclusions and deterministic ordering."""

from __future__ import annotations

import os
from pathlib import Path

from .ignore import Excluder


def walk_repo(repo_path: Path, excluder: Excluder) -> tuple[list[Path], list[Path]]:
    files: list[Path] = []
    dirs: list[Path] = []

    def _walk(current: Path, rel: Path) -> None:
        try:
            with os.scandir(current) as it:
                entries = sorted(it, key=lambda entry: entry.name)
        except OSError as exc:
            raise OSError(f"Failed to scan directory: {current}") from exc

        for entry in entries:
            rel_path = rel / entry.name
            rel_posix = rel_path.as_posix()

            if entry.is_dir(follow_symlinks=False):
                if entry.is_symlink():
                    continue
                if excluder.is_excluded(rel_posix, is_dir=True):
                    continue
                dirs.append(rel_path)
                _walk(Path(entry.path), rel_path)
                continue

            if entry.is_file(follow_symlinks=False):
                if excluder.is_excluded(rel_posix, is_dir=False):
                    continue
                files.append(rel_path)

    _walk(repo_path, Path(""))
    return files, dirs
