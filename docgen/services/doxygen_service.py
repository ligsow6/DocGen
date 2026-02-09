"""Doxygen integration for DocGen."""

from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess

from ..errors import DocGenIOError

_PROJECT_NAME_RE = re.compile(r"^\s*PROJECT_NAME\s*=\s*(.*)$")
_OUTPUT_DIR_RE = re.compile(r"^\s*OUTPUT_DIRECTORY\s*=\s*(.*)$")


def _template_doxyfile_path() -> Path:
    return Path(__file__).resolve().parents[2] / "Doxyfile"


def find_doxyfile(repo_path: Path) -> Path | None:
    """Return the template Doxyfile shipped with DocGen, if available."""
    template = _template_doxyfile_path()
    if template.is_file():
        return template
    candidates = [repo_path / "Doxyfile", repo_path / "docs" / "Doxyfile"]
    for path in candidates:
        if path.is_file():
            return path
    return None


def _render_doxyfile(template: str, project_name: str) -> str:
    replaced = False
    lines: list[str] = []
    for line in template.splitlines():
        match = _PROJECT_NAME_RE.match(line)
        if match:
            lines.append(f'PROJECT_NAME           = "{project_name}"')
            replaced = True
        else:
            lines.append(line)
    if not replaced:
        lines.append(f'PROJECT_NAME           = "{project_name}"')
    return "\n".join(lines) + "\n"


def _ensure_output_dir(repo_path: Path, rendered: str) -> None:
    output_dir = None
    for line in rendered.splitlines():
        match = _OUTPUT_DIR_RE.match(line)
        if not match:
            continue
        raw = match.group(1).strip()
        if raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1]
        if raw:
            output_dir = raw
        break
    if not output_dir:
        return
    output_path = Path(output_dir)
    if not output_path.is_absolute():
        output_path = repo_path / output_path
    output_path.mkdir(parents=True, exist_ok=True)


def run_doxygen(repo_path: Path) -> Path:
    template_path = find_doxyfile(repo_path)
    if not template_path:
        raise DocGenIOError(
            "Doxyfile template not found (expected DocGen Doxyfile or repo Doxyfile)."
        )
    if shutil.which("doxygen") is None:
        raise DocGenIOError("Doxygen not found in PATH. Install it to use --doxygen.")

    project_name = repo_path.name
    template_text = template_path.read_text(encoding="utf-8", errors="ignore")
    rendered = _render_doxyfile(template_text, project_name)
    _ensure_output_dir(repo_path, rendered)
    temp_path = repo_path / ".docgen.Doxyfile"

    try:
        temp_path.write_text(rendered, encoding="utf-8")
        subprocess.run(["doxygen", str(temp_path)], cwd=repo_path, check=True)
    except subprocess.CalledProcessError as exc:
        raise DocGenIOError("Doxygen failed. See output above.") from exc
    finally:
        try:
            if temp_path.exists():
                temp_path.unlink()
        except OSError:
            pass

    return template_path
