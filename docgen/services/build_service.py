"""Build service for DocGen."""

from __future__ import annotations

from dataclasses import dataclass, replace
import os
from pathlib import Path
from typing import Any

from ..config import DocGenConfig
from ..models import DetectedFile, ProjectInfo
from ..errors import ConfigError, DocGenIOError
from ..rendering import render_template, write_text
from ..rendering.markers import apply_all_sections, extract_managed_sections
from ..utils.ignore import build_excluder
from ..services.scan_service import scan_repo, _build_excludes
from ..utils.code_inspect import collect_code_overview
from ..services.doxygen_service import find_doxyfile, run_doxygen


@dataclass(frozen=True)
class BuildPlan:
    targets: list[Path]
    sections: list[str]
    template_map: dict[str, Path]
    reports: dict[Path, "BuildReport"]
    doxygen_requested: bool = False
    doxygen_ran: bool = False
    doxygen_would_run: bool = False
    doxygen_file: Path | None = None


@dataclass(frozen=True)
class BuildReport:
    created: bool = False
    overwritten: bool = False
    replaced: list[str] | None = None
    added: list[str] | None = None
    unchanged: list[str] | None = None


def build_docs(
    repo_path: Path,
    config: DocGenConfig,
    dry_run: bool = False,
    force: bool = False,
    doxygen: bool = False,
) -> BuildPlan:
    if config.readme_target == "root" and config.output_dir not in {".", "./", ""}:
        raise ConfigError("readme_target='root' requires output_dir='.'")
    project = scan_repo(repo_path, config)
    context, sections, template_map = _prepare_context(repo_path, config, project)
    plan = BuildPlan(
        targets=list(template_map.values()),
        sections=sections,
        template_map=template_map,
        reports={},
        doxygen_requested=doxygen,
    )

    for template_name, target in plan.template_map.items():
        content = render_template(template_name, context)
        section_names = [section.name for section in extract_managed_sections(content)]
        role = _file_role(target.name)

        if not target.exists():
            plan.reports[target] = BuildReport(created=True, added=section_names)
            if not dry_run:
                write_text(target, content)
            continue

        if force:
            plan.reports[target] = BuildReport(overwritten=True, added=section_names)
            if not dry_run:
                write_text(target, content)
            continue

        existing = target.read_text(encoding="utf-8")
        updated, report = apply_all_sections(existing, content, role)
        plan.reports[target] = BuildReport(
            replaced=report.replaced,
            added=report.added,
            unchanged=report.unchanged,
        )
        if not dry_run:
            write_text(target, updated)

    if doxygen:
        if dry_run:
            doxyfile = find_doxyfile(repo_path)
            if not doxyfile:
                raise DocGenIOError(
                    "Doxyfile not found (expected Doxyfile or docs/Doxyfile)."
                )
            plan = replace(plan, doxygen_would_run=True, doxygen_file=doxyfile)
        else:
            doxyfile = run_doxygen(repo_path)
            plan = replace(plan, doxygen_ran=True, doxygen_file=doxyfile)

    return plan


def _prepare_context(
    repo_path: Path,
    config: DocGenConfig,
    project: ProjectInfo,
) -> tuple[dict[str, Any], list[str], dict[str, Path]]:
    output_dir = Path(config.output_dir)
    readme_target = config.readme_target

    readme_path = (output_dir / "README.md") if readme_target == "output" else Path("README.md")
    arch_path = output_dir / "ARCHITECTURE.md"
    index_path = output_dir / "index.md"

    readme_link, architecture_link, index_link = _build_links(output_dir, readme_target)

    enable_github_pages = config.enable_github_pages
    enable_doxygen_block = _enable_doxygen_block(config.enable_doxygen_block, project)

    key_files = _filter_key_files(project.files_detected)
    key_files_by_type = _group_files_by_type(key_files)
    ci_files = _ci_files(project.files_detected)
    top_level_dirs = _top_level_dirs(repo_path, config)
    top_level_dirs = _filter_structure_dirs(top_level_dirs)
    top_level_nodes = [_node_from_name(name) for name in top_level_dirs]
    stack_nodes = [_node_from_name(stack.name) for stack in project.stacks]

    context = {
        "project_name": project.project_name,
        "repo_root": project.repo_root,
        "stacks": project.stacks,
        "commands": project.commands,
        "ci": project.ci,
        "ci_files": ci_files,
        "key_files": key_files,
        "key_files_by_type": key_files_by_type,
        "files_detected_count": len(key_files),
        "stacks_count": len(project.stacks),
        "top_level_dirs": top_level_dirs,
        "top_level_nodes": top_level_nodes,
        "stack_nodes": stack_nodes,
        "enable_github_pages": enable_github_pages,
        "enable_doxygen_block": enable_doxygen_block,
        "docker_enabled": any(stack.name == "docker" for stack in project.stacks),
        "readme_link": readme_link,
        "architecture_link": architecture_link,
        "index_link": index_link,
    }

    context.update(collect_code_overview(repo_path, config))

    sections = ["Summary", "Stacks", "Commands", "Structure", "CI", "Documentation"]
    if enable_github_pages:
        sections.append("GitHub Pages")
    if enable_doxygen_block:
        sections.append("Doxygen")

    template_map: dict[str, Path] = {
        "README.md.j2": repo_path / readme_path,
        "ARCHITECTURE.md.j2": repo_path / arch_path,
    }
    if enable_github_pages:
        template_map["INDEX.md.j2"] = repo_path / index_path

    return context, sections, template_map


def _file_role(filename: str) -> str:
    lower = filename.lower()
    if lower == "readme.md":
        return "readme"
    if lower == "architecture.md":
        return "architecture"
    return "index"


def _build_links(output_dir: Path, readme_target: str) -> tuple[str, str, str]:
    output_posix = output_dir.as_posix()
    if output_posix == ".":
        output_posix = ""

    if readme_target == "output":
        readme_link = "README.md"
        architecture_link = "ARCHITECTURE.md"
        index_link = "index.md"
        return readme_link, architecture_link, index_link

    prefix = f"{output_posix}/" if output_posix else ""
    readme_link = "../README.md" if output_posix else "README.md"
    architecture_link = f"{prefix}ARCHITECTURE.md"
    index_link = f"{prefix}index.md"
    return readme_link, architecture_link, index_link


def _enable_doxygen_block(setting: str | bool, project: ProjectInfo) -> bool:
    if isinstance(setting, bool):
        return setting
    has_doxygen = any(item.type == "doxygen" for item in project.files_detected)
    return has_doxygen


def _filter_key_files(files: list[DetectedFile]) -> list[DetectedFile]:
    filtered = [
        item
        for item in files
        if item.type not in {"readme", "docs_dir"}
    ]
    return sorted(filtered, key=lambda item: (item.type, item.path))


def _group_files_by_type(files: list[DetectedFile]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for item in files:
        grouped.setdefault(item.type, []).append(item.path)
    for items in grouped.values():
        items.sort()
    return dict(sorted(grouped.items()))


def _ci_files(files: list[DetectedFile]) -> list[str]:
    ci_types = {"github_actions", "gitlab_ci", "jenkins"}
    paths = [item.path for item in files if item.type in ci_types]
    return sorted(paths)


def _top_level_dirs(repo_path: Path, config: DocGenConfig) -> list[str]:
    patterns = _build_excludes(config.exclude, config.output_dir)
    excluder = build_excluder(patterns)

    names: list[str] = []
    with os.scandir(repo_path) as it:
        for entry in it:
            if not entry.is_dir(follow_symlinks=False):
                continue
            rel = entry.name
            rel_posix = rel.replace("\\", "/")
            if excluder.is_excluded(rel_posix, is_dir=True):
                continue
            names.append(entry.name)
    return sorted(set(names))


def _filter_structure_dirs(names: list[str]) -> list[str]:
    banned = {"docs", "docgen", "documentation"}
    names = [name for name in names if name.lower() not in banned]
    allowlist = {
        "src",
        "app",
        "apps",
        "packages",
        "services",
        "libs",
        "lib",
        "tests",
        "test",
        "infra",
        "docker",
        "scripts",
        "config",
        "configs",
        "backend",
        "frontend",
        "client",
        "server",
        "api",
    }
    filtered = [name for name in names if name in allowlist]
    if filtered:
        return sorted(filtered)
    return sorted(names)


def _node_from_name(name: str) -> dict[str, str]:
    safe = "".join(ch if ch.isalnum() else "_" for ch in name.lower())
    if not safe:
        safe = "node"
    return {"id": safe, "label": f"{name}/"}
