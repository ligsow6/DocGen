from pathlib import Path

from docgen.config import DEFAULT_EXCLUDE, DocGenConfig, load_config


def test_load_config_merges_defaults(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    config_path = repo / "docgen.yaml"
    config_path.write_text("output_dir: out\n", encoding="utf-8")

    config = load_config(repo)

    assert isinstance(config, DocGenConfig)
    assert config.output_dir == "out"
    assert config.exclude == DEFAULT_EXCLUDE


def test_load_config_overrides_exclude(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    config_path = repo / "docgen.yaml"
    config_path.write_text(
        "output_dir: DocGen\nexclude:\n  - custom/\n  - vendor/\n",
        encoding="utf-8",
    )

    config = load_config(repo)

    assert config.output_dir == "DocGen"
    assert config.exclude == ["custom/", "vendor/"]
