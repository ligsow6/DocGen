"""Template rendering helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .errors import DocGenIOError


def _template_dir() -> Path:
    return Path(__file__).parent / "templates"


def create_environment() -> Environment:
    loader = FileSystemLoader(str(_template_dir()))
    return Environment(
        loader=loader,
        autoescape=select_autoescape(enabled_extensions=()),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_template(name: str, context: dict[str, Any]) -> str:
    env = create_environment()
    template = env.get_template(name)
    return template.render(**context).strip() + "\n"


def write_text(path: Path, content: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise DocGenIOError(f"Failed to write file: {path}") from exc
