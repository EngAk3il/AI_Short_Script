"""Validate generated scripts for retention, DNA, and structure."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

FORBIDDEN_OPENERS = [
    "aaj hum baat karenge",
    "hey guys",
    "welcome back",
    "namaste dosto aaj",
    "is video mein hum",
]

REQUIRED_SECTIONS = [
    (
        "script",
        re.compile(
            r"\|[^\n]*Timestamp[^\n]*\||##\s*SCRIPT|##\s*FULL SCRIPT|\[00:\d{2}\]|0:00\s*to",
            re.I,
        ),
    ),
    ("dna_audit", re.compile(r"DNA\s+(Adherence\s+)?Audit|### DNA Audit", re.I)),
    ("retention", re.compile(r"WATCH-THROUGH|RETENTION|5-PHASE|PHASE 1|WHY THIS SCRIPT", re.I)),
    ("references", re.compile(r"References|📚", re.I)),
]

HOOK_META = re.compile(r"\[HOOK TYPE(?: USED)?:\s*([^\]]+)\]", re.I)


@dataclass
class ScriptValidation:
    passed: bool
    score: int = 0
    max_score: int = 100
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def feedback_for_retry(self) -> str:
        parts = ["Fix these validation failures:"]
        parts.extend(f"- {e}" for e in self.errors)
        parts.extend(f"- (warning) {w}" for w in self.warnings)
        return "\n".join(parts)


def _count_table_rows(markdown: str) -> int:
    rows = 0
    in_table = False
    for line in markdown.splitlines():
        if "|" in line and "Timestamp" in line:
            in_table = True
            continue
        if in_table:
            if line.strip().startswith("|") and "---" not in line:
                if "Timestamp" not in line:
                    rows += 1
            elif in_table and line.strip() and not line.strip().startswith("|"):
                break
    return rows


def validate_script(markdown: str, creator: str = "") -> ScriptValidation:
    v = ScriptValidation(passed=True, max_score=100)
    text_lower = markdown.lower()
    score = 0

    # Forbidden openers in first 500 chars
    head = text_lower[:500]
    for phrase in FORBIDDEN_OPENERS:
        if phrase in head:
            v.passed = False
            v.errors.append(f"Forbidden opener phrase: '{phrase}'")

    # Required sections
    for name, pattern in REQUIRED_SECTIONS:
        if pattern.search(markdown):
            score += 20
        else:
            v.passed = False
            v.errors.append(f"Missing required section: {name}")

    # Hook metadata
    if HOOK_META.search(markdown) or re.search(r"Hook Type:\s*\S+", markdown, re.I):
        score += 10
    else:
        v.warnings.append("No explicit HOOK TYPE metadata — add [HOOK TYPE: ...] at top")

    rows = _count_table_rows(markdown)
    timestamp_markers = len(re.findall(r"\[00:\d{2}\]|0:\d{2}\s*to|0:\d{2}\s*—", markdown))
    if rows >= 6 or timestamp_markers >= 4:
        score += 20
    else:
        v.passed = False
        v.errors.append(
            f"Need ≥6 table rows or ≥4 timestamp sections; rows={rows}, markers={timestamp_markers}"
        )

    # Status
    if "PRODUCTION READY" in markdown or "Status:" in markdown:
        score += 10

    # Unverified markers
    if "[UNVERIFIED" in markdown:
        v.passed = False
        v.errors.append("Contains [UNVERIFIED] markers — research or remove claims")

    v.score = min(score, v.max_score)
    if v.score < 60 and v.passed:
        v.warnings.append(f"Retention quality score low: {v.score}/100")

    return v
