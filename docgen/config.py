"""Configuration handling for DocGen."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .errors import ConfigError, DocGenIOError

DEFAULT_OUTPUT_DIR = "docs"
DEFAULT_EXCLUDE = [".git/", "node_modules/", "dist/", "build/"]


@dataclass(frozen=True)
class DocGenConfig:
    output_dir: str = DEFAULT_OUTPUT_DIR
    exclude: list[str] = field(default_factory=lambda: list(DEFAULT_EXCLUDE))

    def to_dict(self) -> dict[str, Any]:
        return {"output_dir": self.output_dir, "exclude": list(self.exclude)}


def default_config() -> DocGenConfig:
    return DocGenConfig()


def resolve_config_path(repo_path: Path, config_path: Path | None) -> Path:
    if config_path is None:
        return (repo_path / "docgen.yaml").expanduser().resolve()
    return config_path.expanduser().resolve()


def load_config(
    repo_path: Path,
    config_path: Path | None = None,
    require_exists: bool = False,
) -> DocGenConfig:
    path = resolve_config_path(repo_path, config_path)
    if not path.exists():
        if require_exists:
            raise ConfigError(f"Config file not found: {path}")
        return default_config()
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except OSError as exc:
        raise DocGenIOError(f"Failed to read config: {path}") from exc
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in config: {path}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"Config must be a mapping: {path}")
    return validate_config(data)


def validate_config(data: dict[str, Any]) -> DocGenConfig:
    allowed_keys = {"output_dir", "exclude"}
    unknown = set(data.keys()) - allowed_keys
    if unknown:
        raise ConfigError(f"Unknown config keys: {', '.join(sorted(unknown))}")

    output_dir = data.get("output_dir", DEFAULT_OUTPUT_DIR)
    if not isinstance(output_dir, str) or not output_dir.strip():
        raise ConfigError("output_dir must be a non-empty string")

    exclude = data.get("exclude", DEFAULT_EXCLUDE)
    if not isinstance(exclude, list) or not all(isinstance(item, str) for item in exclude):
        raise ConfigError("exclude must be a list of strings")

    return DocGenConfig(output_dir=output_dir, exclude=list(exclude))


def write_config(path: Path, config: DocGenConfig, overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        raise ConfigError(f"Config file already exists: {path}")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        content = yaml.safe_dump(config.to_dict(), sort_keys=False)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise DocGenIOError(f"Failed to write config: {path}") from exc
