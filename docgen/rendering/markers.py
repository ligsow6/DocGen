"""Managed section markers and idempotent updates."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from ..errors import UsageError

NAME_PATTERN = r"[a-zA-Z0-9_.-]+"
START_RE = re.compile(rf"<!--\s*DOCGEN:START\s+({NAME_PATTERN})\s*-->")
END_RE = re.compile(rf"<!--\s*DOCGEN:END\s+({NAME_PATTERN})\s*-->")
SECTION_RE = re.compile(
    rf"(?P<start><!--\s*DOCGEN:START\s+(?P<section>{NAME_PATTERN})\s*-->)"
    rf"(?P<body>.*?)(?P<end><!--\s*DOCGEN:END\s+(?P=section)\s*-->)",
    re.DOTALL,
)


@dataclass(frozen=True)
class SectionBlock:
    name: str
    start: str
    body: str
    end: str

    @property
    def block(self) -> str:
        return f"{self.start}{self.body}{self.end}"


@dataclass
class UpdateReport:
    replaced: list[str]
    added: list[str]
    unchanged: list[str]


def extract_managed_sections(text: str) -> list[SectionBlock]:
    sections: list[SectionBlock] = []
    for match in SECTION_RE.finditer(text):
        name = match.group("section")
        sections.append(
            SectionBlock(
                name=name,
                start=match.group("start"),
                body=match.group("body"),
                end=match.group("end"),
            )
        )
    return sections


def validate_markers(text: str) -> None:
    starts = START_RE.findall(text)
    ends = END_RE.findall(text)

    for name in set(starts + ends):
        if starts.count(name) != ends.count(name):
            raise UsageError(f"Marker mismatch for section: {name}")
        if starts.count(name) > 1:
            raise UsageError(f"Duplicate section markers found: {name}")


def replace_section(text: str, section: SectionBlock) -> tuple[str, str]:
    escaped = re.escape(section.name)
    pattern = re.compile(
        rf"(?P<start><!--\s*DOCGEN:START\s+{escaped}\s*-->)"
        rf"(?P<body>.*?)(?P<end><!--\s*DOCGEN:END\s+{escaped}\s*-->)",
        re.DOTALL,
    )

    match = pattern.search(text)
    if not match:
        return text, "missing"

    existing_body = match.group("body")
    new_body = _normalize_body(section.body)
    if _normalize_body(existing_body) == new_body:
        return text, "unchanged"
    replacement = f"{match.group('start')}{new_body}{match.group('end')}"
    return text[: match.start()] + replacement + text[match.end() :], "replaced"


def apply_all_sections(
    existing_text: str,
    rendered_template: str,
    file_role: str,
) -> tuple[str, UpdateReport]:
    validate_markers(existing_text)
    template_sections = extract_managed_sections(rendered_template)
    report = UpdateReport(replaced=[], added=[], unchanged=[])

    updated_text = existing_text
    existing_names = {section.name for section in extract_managed_sections(existing_text)}

    missing: list[SectionBlock] = []
    for section in template_sections:
        if section.name not in existing_names:
            missing.append(section)
            continue
        updated_text, status = replace_section(updated_text, section)
        if status == "replaced":
            report.replaced.append(section.name)
        elif status == "unchanged":
            report.unchanged.append(section.name)

    if missing:
        updated_text = _insert_sections(updated_text, missing, file_role)
        report.added.extend([section.name for section in missing])

    return updated_text, report


def _insert_sections(text: str, sections: Iterable[SectionBlock], file_role: str) -> str:
    insertion_point = None
    if file_role == "readme":
        insertion_point = _after_first_title(text)
    elif file_role == "index":
        insertion_point = _after_front_matter_or_title(text)

    combined = "\n\n".join(_ensure_block_spacing(section.block).strip("\n") for section in sections)
    block = combined.strip("\n")

    if insertion_point is None:
        return text.rstrip() + "\n\n" + block + "\n"

    return text[:insertion_point] + block + "\n" + text[insertion_point:]


def _after_first_title(text: str) -> int | None:
    match = re.search(r"^#\s+.+$", text, re.MULTILINE)
    if not match:
        return None
    idx = match.end()
    while idx < len(text) and text[idx] == "\n":
        idx += 1
    return idx


def _after_front_matter_or_title(text: str) -> int | None:
    if text.startswith("---"):
        lines = text.splitlines(keepends=True)
        if lines and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    return sum(len(line) for line in lines[: i + 1])
    return _after_first_title(text)


def _normalize_body(body: str) -> str:
    return "\n" + body.strip("\n") + "\n"


def _ensure_block_spacing(block: str) -> str:
    return block.strip("\n") + "\n"
