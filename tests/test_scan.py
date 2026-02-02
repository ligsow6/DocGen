from __future__ import annotations

from pathlib import Path
import json

from typer.testing import CliRunner

from docgen.cli import app
from docgen.config import DocGenConfig
from docgen.services.scan_service import scan_repo


FIXTURES = Path(__file__).parent / "fixtures"
runner = CliRunner()


def test_scan_repo_node_detects_key_files_and_excludes() -> None:
    repo_path = FIXTURES / "repo_node"
    project = scan_repo(repo_path, DocGenConfig())

    paths = {item.path for item in project.files_detected}

    assert "package.json" in paths
    assert "package-lock.json" in paths
    assert "tsconfig.json" in paths
    assert ".github/workflows/ci.yml" in paths

    assert "node_modules/package.json" not in paths
    assert "docs/README.md" not in paths

    assert "node" in project.stacks
    assert "github_actions" in project.ci


def test_scan_repo_python_detects_key_files() -> None:
    repo_path = FIXTURES / "repo_python"
    project = scan_repo(repo_path, DocGenConfig())

    paths = {item.path for item in project.files_detected}

    assert "pyproject.toml" in paths
    assert "requirements.txt" in paths
    assert ".gitlab-ci.yml" in paths

    assert "python" in project.stacks
    assert "gitlab_ci" in project.ci


def test_scan_repo_docker_detects_key_files() -> None:
    repo_path = FIXTURES / "repo_docker"
    project = scan_repo(repo_path, DocGenConfig())

    paths = {item.path for item in project.files_detected}

    assert "Dockerfile" in paths
    assert "docker-compose.yml" in paths
    assert "Jenkinsfile" in paths
    assert "Doxyfile" in paths

    assert "docker" in project.stacks
    assert "jenkins" in project.ci


def test_scan_cli_json_output_sorted() -> None:
    repo_path = FIXTURES / "repo_node"
    result = runner.invoke(app, ["scan", "--repo", str(repo_path), "--format", "json"])

    assert result.exit_code == 0

    payload = json.loads(result.stdout)
    paths = [item["path"] for item in payload["files_detected"]]

    assert paths == sorted(paths)
    assert all("\\" not in path for path in paths)
