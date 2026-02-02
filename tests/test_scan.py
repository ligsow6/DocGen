from __future__ import annotations

from pathlib import Path
import json

from typer.testing import CliRunner

from docgen.cli import app
from docgen.config import DocGenConfig
from docgen.services.scan_service import scan_repo


FIXTURES = Path(__file__).parent / "fixtures"
runner = CliRunner()


def _stack_names(project) -> set[str]:
    return {stack.name for stack in project.stacks}


def test_scan_repo_node_detects_key_files_and_excludes() -> None:
    repo_path = FIXTURES / "repo_node"
    project = scan_repo(repo_path, DocGenConfig())

    paths = {item.path for item in project.files_detected}

    assert "package.json" in paths
    assert "yarn.lock" in paths
    assert "tsconfig.json" in paths
    assert ".github/workflows/ci.yml" in paths

    assert "node_modules/package.json" not in paths
    assert "docs/README.md" not in paths

    assert "node" in _stack_names(project)
    assert project.package_manager == "yarn"

    assert project.commands.run == "yarn dev"
    assert project.commands.test == "yarn test"
    assert project.commands.lint == "yarn lint"
    assert project.commands.build == "yarn build"


def test_scan_repo_python_detects_key_files_and_commands() -> None:
    repo_path = FIXTURES / "repo_python"
    project = scan_repo(repo_path, DocGenConfig())

    paths = {item.path for item in project.files_detected}

    assert "pyproject.toml" in paths
    assert "requirements.txt" in paths
    assert ".gitlab-ci.yml" in paths

    assert "python" in _stack_names(project)
    assert project.python_tooling == "poetry"

    assert project.commands.test == "poetry run pytest"
    assert project.commands.lint == "poetry run ruff check ."


def test_scan_repo_docker_detects_key_files_and_commands() -> None:
    repo_path = FIXTURES / "repo_docker"
    project = scan_repo(repo_path, DocGenConfig())

    paths = {item.path for item in project.files_detected}

    assert "Dockerfile" in paths
    assert "docker-compose.yml" in paths
    assert "Jenkinsfile" in paths
    assert "Doxyfile" in paths

    assert "docker" in _stack_names(project)
    assert "jenkins" in project.ci

    assert project.commands.run == "docker compose up --build"
    assert project.commands.build == "docker compose build"


def test_scan_repo_multi_detects_multiple_stacks_and_commands() -> None:
    repo_path = FIXTURES / "repo_multi"
    project = scan_repo(repo_path, DocGenConfig())

    assert _stack_names(project) == {"node", "python", "docker"}
    assert project.package_manager == "npm"

    assert project.commands.run == "npm run start"
    assert project.commands.test == "npm run test"
    assert project.commands.lint == "npm run lint"
    assert project.commands.build == "npm run build"


def test_scan_cli_json_output_sorted() -> None:
    repo_path = FIXTURES / "repo_node"
    result = runner.invoke(app, ["scan", "--repo", str(repo_path), "--format", "json"])

    assert result.exit_code == 0

    payload = json.loads(result.stdout)
    paths = [item["path"] for item in payload["files_detected"]]
    stack_names = [item["name"] for item in payload["stacks"]]

    assert paths == sorted(paths)
    assert stack_names == sorted(stack_names)
    assert all("\\" not in path for path in paths)
