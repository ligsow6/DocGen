from pathlib import Path

import yaml
from typer.testing import CliRunner

from docgen.cli import app
from docgen.config import DEFAULT_EXCLUDE, DEFAULT_OUTPUT_DIR


runner = CliRunner()


def test_init_creates_config_and_output_dir(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = runner.invoke(app, ["init", "--repo", str(repo)])

    assert result.exit_code == 0

    config_path = repo / "docgen.yaml"
    assert config_path.exists()

    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert data["output_dir"] == DEFAULT_OUTPUT_DIR
    assert data["exclude"] == DEFAULT_EXCLUDE
    assert data["readme_target"] == "output"
    assert data["enable_github_pages"] is True
    assert data["enable_doxygen_block"] == "auto"

    output_dir = repo / DEFAULT_OUTPUT_DIR
    assert output_dir.exists()
    assert (output_dir / "README.md").exists()
    assert (output_dir / "ARCHITECTURE.md").exists()
