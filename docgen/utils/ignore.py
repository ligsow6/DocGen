"""Simple exclusion matcher for repository walking."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Excluder:
    dir_names: frozenset[str]
    dir_prefixes: tuple[str, ...]
    file_names: frozenset[str]
    path_prefixes: tuple[str, ...]

    def is_excluded(self, rel_path: str, is_dir: bool) -> bool:
        parts = rel_path.split("/") if rel_path else []

        if self.dir_names and any(part in self.dir_names for part in parts):
            return True

        if not is_dir and self.file_names:
            name = parts[-1] if parts else rel_path
            if name in self.file_names:
                return True

        for prefix in self.path_prefixes:
            if rel_path == prefix or rel_path.startswith(prefix + "/"):
                return True

        for prefix in self.dir_prefixes:
            if rel_path == prefix or rel_path.startswith(prefix + "/"):
                return True

        return False


def _normalize_pattern(pattern: str) -> str:
    normalized = pattern.strip().replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def build_excluder(patterns: list[str]) -> Excluder:
    dir_names: set[str] = set()
    dir_prefixes: set[str] = set()
    file_names: set[str] = set()
    path_prefixes: set[str] = set()

    for raw in patterns:
        normalized = _normalize_pattern(raw)
        if not normalized:
            continue

        if normalized.endswith("/"):
            trimmed = normalized.rstrip("/")
            if not trimmed:
                continue
            if "/" in trimmed:
                dir_prefixes.add(trimmed)
            else:
                dir_names.add(trimmed)
            continue

        if "/" in normalized:
            path_prefixes.add(normalized)
        else:
            file_names.add(normalized)

    return Excluder(
        dir_names=frozenset(dir_names),
        dir_prefixes=tuple(sorted(dir_prefixes)),
        file_names=frozenset(file_names),
        path_prefixes=tuple(sorted(path_prefixes)),
    )
