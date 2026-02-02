"""Data models for DocGen."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any


@dataclass(frozen=True)
class StackInfo:
    name: str
    confidence: float
    evidence: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)

    def as_label(self) -> str:
        return self.name

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "confidence": self.confidence,
            "evidence": list(self.evidence),
            "attributes": dict(self.attributes),
        }


@dataclass(frozen=True)
class DetectedFile:
    path: str
    type: str

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "type": self.type}


@dataclass(frozen=True)
class Commands:
    run: str | None = None
    test: str | None = None
    lint: str | None = None
    build: str | None = None
    format: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "run": self.run,
            "test": self.test,
            "lint": self.lint,
            "build": self.build,
            "format": self.format,
        }


@dataclass(frozen=True)
class DocsInfo:
    readme_path: str
    architecture_path: str
    github_pages_dir: str | None = None
    doxygen_dir: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "readme_path": self.readme_path,
            "architecture_path": self.architecture_path,
            "github_pages_dir": self.github_pages_dir,
            "doxygen_dir": self.doxygen_dir,
        }


@dataclass(frozen=True)
class ProjectInfo:
    project_name: str
    repo_root: str
    stacks: list[StackInfo]
    files_detected: list[DetectedFile]
    commands: Commands
    ci: list[str]
    docs: DocsInfo
    package_manager: str | None = None
    python_tooling: str | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "repo_root": self.repo_root,
            "stacks": [stack.to_dict() for stack in self.stacks],
            "files_detected": [item.to_dict() for item in self.files_detected],
            "commands": self.commands.to_dict(),
            "ci": list(self.ci),
            "docs": self.docs.to_dict(),
            "package_manager": self.package_manager,
            "python_tooling": self.python_tooling,
            "warnings": list(self.warnings),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)
