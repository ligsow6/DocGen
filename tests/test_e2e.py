from __future__ import annotations

from pathlib import Path
import json
import shutil

from typer.testing import CliRunner

from docgen.cli import app


FIXTURES = Path(__file__).parent / "fixtures"
runner = CliRunner()


def _copy_fixture(tmp_path: Path, name: str) -> Path:
    src = FIXTURES / name
    dest = tmp_path / name
    shutil.copytree(src, dest)
    return dest


def test_e2e_scan_build_idempotent(tmp_path: Path) -> None:
    repo_path = _copy_fixture(tmp_path, "repo_multi")

    scan_result = runner.invoke(app, ["scan", "--repo", str(repo_path), "--format", "json"])
    assert scan_result.exit_code == 0
    payload = json.loads(scan_result.stdout)
    assert payload["project_name"] == "repo_multi"

    build_result = runner.invoke(app, ["build", "--repo", str(repo_path)])
    assert build_result.exit_code == 0

    readme_path = repo_path / "docs" / "README.md"
    arch_path = repo_path / "docs" / "ARCHITECTURE.md"
    index_path = repo_path / "docs" / "index.md"

    assert readme_path.exists()
    assert arch_path.exists()
    assert index_path.exists()

    first = readme_path.read_text(encoding="utf-8")

    build_again = runner.invoke(app, ["build", "--repo", str(repo_path)])
    assert build_again.exit_code == 0

    second = readme_path.read_text(encoding="utf-8")
    assert first == second
