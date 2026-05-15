"""Validate per-transcript entries in deep_hooks.md."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# Matches: ## #12 | video_id | GENRE: ...
ENTRY_HEADER = re.compile(
    r"^##\s*#(\d+)\s*\|\s*([^\s|]+)\s*\|\s*GENRE:\s*(.+)$",
    re.M | re.I,
)

REQUIRED_FIELDS = [
    "HOOK TYPE",
    "EXACT HOOK",
    "NARRATIVE PATTERN",
    "TEMPLATE EXTRACT",
]


@dataclass
class HookLibraryValidation:
    passed: bool
    entries_found: int = 0
    entries_complete: int = 0
    transcript_count: int = 0
    missing_videos: list[str] = field(default_factory=list)
    incomplete_entries: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def validate_deep_hooks_content(
    content: str,
    expected_transcript_count: int,
    video_ids: list[str] | None = None,
) -> HookLibraryValidation:
    v = HookLibraryValidation(
        passed=True,
        transcript_count=expected_transcript_count,
    )

    headers = list(ENTRY_HEADER.finditer(content))
    v.entries_found = len(headers)

    if expected_transcript_count > 0 and v.entries_found < expected_transcript_count * 0.8:
        v.passed = False
        v.errors.append(
            f"Only {v.entries_found}/{expected_transcript_count} per-transcript entries "
            "(expected ≥80% coverage)"
        )

    found_ids = {m.group(2) for m in headers}
    if video_ids:
        for vid in video_ids:
            if vid not in found_ids:
                v.missing_videos.append(vid)

    # Check each entry block for required fields
    for i, m in enumerate(headers):
        start = m.start()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(content)
        block = content[start:end]
        vid = m.group(2)
        missing = []
        block_upper = block.upper()
        for field_name in REQUIRED_FIELDS:
            if field_name.upper() not in block_upper:
                missing.append(field_name)
        if missing:
            v.incomplete_entries.append(f"{vid}: missing {', '.join(missing)}")
        else:
            v.entries_complete += 1

    if v.incomplete_entries:
        v.passed = False
        v.errors.append(
            f"{len(v.incomplete_entries)} entries missing required fields "
            f"(HOOK TYPE, EXACT HOOK, NARRATIVE PATTERN, TEMPLATE EXTRACT)"
        )

    if not re.search(r"MASTER HOOK LIBRARY", content, re.I):
        v.errors.append("Missing MASTER HOOK LIBRARY summary section")
        v.passed = False

    return v
