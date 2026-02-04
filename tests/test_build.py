from __future__ import annotations

from pathlib import Path
import shutil

from docgen.config import DocGenConfig
from docgen.services.build_service import build_docs


FIXTURES = Path(__file__).parent / "fixtures"


def _copy_fixture(tmp_path: Path, name: str) -> Path:
    src = FIXTURES / name
    dest = tmp_path / name
    shutil.copytree(src, dest)
    return dest


def test_build_creates_files_in_output_dir(tmp_path: Path) -> None:
    repo_path = _copy_fixture(tmp_path, "repo_node")
    config = DocGenConfig(output_dir="generated-docs", readme_target="output")

    plan = build_docs(repo_path, config)

    output_dir = repo_path / "generated-docs"
    readme_path = output_dir / "README.md"
    architecture_path = output_dir / "ARCHITECTURE.md"
    index_path = output_dir / "index.md"

    assert readme_path.exists()
    assert architecture_path.exists()
    assert index_path.exists()

    content = readme_path.read_text(encoding="utf-8")
    assert "Stacks detectees" in content
    assert "Commandes" in content

    assert all(path.exists() for path in plan.targets)


def test_build_readme_target_root(tmp_path: Path) -> None:
    repo_path = _copy_fixture(tmp_path, "repo_python")
    config = DocGenConfig(output_dir="docs-out", readme_target="root")

    build_docs(repo_path, config)

    readme_path = repo_path / "README.md"
    architecture_path = repo_path / "docs-out" / "ARCHITECTURE.md"
    index_path = repo_path / "docs-out" / "index.md"

    assert readme_path.exists()
    assert architecture_path.exists()
    assert index_path.exists()


def test_build_updates_existing_markers_preserves_manual(tmp_path: Path) -> None:
    repo_path = _copy_fixture(tmp_path, "repo_node")
    config = DocGenConfig(output_dir="docs", readme_target="output")

    build_docs(repo_path, config, force=True)

    readme_path = repo_path / "docs" / "README.md"
    content = readme_path.read_text(encoding="utf-8")
    assert "Documentation generee automatiquement" in content

    updated = "MANUAL TOP\n\n" + content + "\nMANUAL BOTTOM\n"
    updated = updated.replace(
        "Documentation generee automatiquement a partir du depot.",
        "CUSTOM SUMMARY",
    )
    readme_path.write_text(updated, encoding="utf-8")

    build_docs(repo_path, config)

    refreshed = readme_path.read_text(encoding="utf-8")
    assert "MANUAL TOP" in refreshed
    assert "MANUAL BOTTOM" in refreshed
    assert "CUSTOM SUMMARY" not in refreshed
    assert "Documentation generee automatiquement" in refreshed


def test_build_inserts_markers_when_missing(tmp_path: Path) -> None:
    repo_path = _copy_fixture(tmp_path, "repo_python")
    config = DocGenConfig(output_dir="docs", readme_target="output")

    output_dir = repo_path / "docs"
    output_dir.mkdir(parents=True, exist_ok=True)
    readme_path = output_dir / "README.md"
    readme_path.write_text("# Manual Title\n\nManual notes here.\n", encoding="utf-8")

    build_docs(repo_path, config)

    content = readme_path.read_text(encoding="utf-8")
    assert "Manual notes here." in content
    assert "<!-- DOCGEN:START summary -->" in content
    assert "<!-- DOCGEN:END summary -->" in content


def test_build_force_overwrites(tmp_path: Path) -> None:
    repo_path = _copy_fixture(tmp_path, "repo_multi")
    config = DocGenConfig(output_dir="docs", readme_target="output")

    output_dir = repo_path / "docs"
    output_dir.mkdir(parents=True, exist_ok=True)
    readme_path = output_dir / "README.md"
    readme_path.write_text("# Manual\nDo not keep this.\n", encoding="utf-8")

    build_docs(repo_path, config, force=True)

    content = readme_path.read_text(encoding="utf-8")
    assert "Do not keep this" not in content
    assert "<!-- DOCGEN:START summary -->" in content


def test_build_dry_run_does_not_write(tmp_path: Path) -> None:
    repo_path = _copy_fixture(tmp_path, "repo_multi")
    config = DocGenConfig(output_dir="out", readme_target="output")

    plan = build_docs(repo_path, config, dry_run=True)

    assert not (repo_path / "out").exists()
    for target in plan.targets:
        assert not target.exists()
