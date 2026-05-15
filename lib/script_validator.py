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
    ("hook_pattern", re.compile(r"##\s*HOOK\s+PATTERN", re.I)),
    (
        "reference_transcript",
        re.compile(r"##\s*REFERENCE\s+TRANSCRIPT|What we took from this transcript", re.I),
    ),
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
    neha_script_ok = creator == "NehaGupta" and re.search(
        r"Director:|^```", markdown, re.M | re.I
    )
    for name, pattern in REQUIRED_SECTIONS:
        if pattern.search(markdown) or (name == "script" and neha_script_ok):
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
    fenced_lines = len(re.findall(r"^```", markdown, re.M))
    director_blocks = len(re.findall(r"\*\*\[Director:", markdown, re.I))
    neha_style = creator == "NehaGupta" and (
        fenced_lines >= 2 or director_blocks >= 2 or len(re.findall(r"^```", markdown, re.M)) >= 8
    )
    script_section = bool(
        re.search(r"##\s*SCRIPT|```\n|Director:", markdown, re.I)
    )
    if rows >= 6 or timestamp_markers >= 4 or neha_style or (creator == "NehaGupta" and script_section):
        score += 20
    else:
        v.passed = False
        v.errors.append(
            f"Need ≥6 table rows, ≥4 timestamps, or NehaGupta director/script blocks; "
            f"rows={rows}, markers={timestamp_markers}, fenced={fenced_lines}"
        )

    if creator:
        try:
            from lib.script_formats import check_voice_markers

            voice_errors = check_voice_markers(markdown, creator)
            for err in voice_errors:
                if "exact CTA" in err or "Forbidden" in err:
                    v.passed = False
                    v.errors.append(err)
                else:
                    v.warnings.append(err)
        except ImportError:
            pass

    # Status
    if "PRODUCTION READY" in markdown or "Status:" in markdown:
        score += 10

    # Unverified markers
    if "[UNVERIFIED" in markdown:
        v.passed = False
        v.errors.append("Contains [UNVERIFIED] markers — research or remove claims")

    # Date spam in spoken script (wire-copy anti-pattern)
    script_body = markdown
    if "## FULL SCRIPT" in markdown:
        script_body = markdown.split("## FULL SCRIPT", 1)[-1].split("###", 1)[0]
    elif "## SCRIPT" in markdown:
        script_body = markdown.split("## SCRIPT", 1)[-1].split("###", 1)[0]
    date_hits = len(
        re.findall(
            r"\b20\d{2}\b|"
            r"\b\d{1,2}\s+may\s+20\d{2}\b|"
            r"\bmay\s+\d{1,2},?\s+20\d{2}\b|"
            r"14\s+may|15\s+may|may\s+14|may\s+15",
            script_body,
            re.I,
        )
    )
    if date_hits >= 3:
        v.warnings.append(
            f"Date spam detected ({date_hits} calendar refs in script) — "
            "match reference transcript (usually 0–1 dates in speech). See CREATOR_SCRIPT_INTELLIGENCE.md"
        )

    # Retention map: viewer question column (Rule 2f)
    if re.search(r"WATCH-THROUGH", markdown, re.I):
        if not re.search(
            r"viewer\s+question|why\s+they\s+stay|दर्शक\s+सोच",
            markdown,
            re.I,
        ):
            v.warnings.append(
                "WATCH-THROUGH MAP missing 'Viewer question (why they stay)' column — see SCRIPT_RULES.md Rule 2f"
            )

    # DNA audit: opening mimics line (Rule 2e)
    if re.search(r"DNA\s+(Adherence\s+)?Audit", markdown, re.I):
        if not re.search(r"opening\s+mimics\s*:", markdown, re.I):
            v.warnings.append(
                "DNA Adherence Audit must include: Opening mimics: \"<ref>\" → \"<script>\""
            )

    # Headline-stack heuristic: many money stats, weak teaching connectors
    teaching_markers = len(
        re.findall(
            r"जब|मतलब|इसीलिए|लेकिन|तो\s+लगता|ने\s+देखा|इस\s+तरह\s+से|सरप्राइज़",
            script_body,
        )
    )
    money_stat_lines = len(
        re.findall(
            r"^\[00:\d{2}\].*(?:₹|Rs\.?|\$|\d+\s*करोड़|\d+\s*लाख)",
            script_body,
            re.I | re.M,
        )
    )
    if money_stat_lines >= 3 and teaching_markers < 2:
        v.warnings.append(
            "Possible headline stack: many ₹/stat lines but few teaching connectors "
            "(जब/मतलब/लेकिन/इसीलिए). Teach one chain — see SCRIPT_RULES.md Rule 2f"
        )

    # Viral STOP: first [00:00] line length and shock markers (Rule 2h)
    first_line_m = re.search(r"^\[00:00\]\s*(.+)$", script_body, re.M)
    if first_line_m:
        first_line = first_line_m.group(1).strip()
        first_words = first_line.split()
        shock_markers = re.search(
            r"!|₹|Rs\.?|\$|\d+\s*करोड़|सबसे|शॉक|सरप्राइज़|धोखा|स्कैम|आखिर|पहली बार|"
            r"इस तरह से|किल किया|टूट|गिरा|रोक|बंद|असंवैधानिक|घाटा|नुकसान",
            first_line,
            re.I,
        )
        if len(first_words) > 22:
            v.warnings.append(
                f"Viral STOP weak: line 1 has {len(first_words)} words (target ≤14 punch + breath). "
                "See SCRIPT_RULES.md Rule 2h"
            )
        if not shock_markers:
            v.warnings.append(
                "Viral STOP weak: line 1 missing shock marker (₹, !, paradox, आखिर, सरप्राइज़). Rule 2h"
            )
    if script_body and not re.search(r"लेकिन\s+असली|लेकिन\s+असल", script_body, re.I):
        v.warnings.append(
            "Missing viral TWIST phrase (लेकिन असली / लेकिन असल). See SCRIPT_RULES.md Rule 2h"
        )

    # Roman-heavy script body
    devanagari = len(re.findall(r"[\u0900-\u097F]", script_body))
    latin_words = len(re.findall(r"\b[a-zA-Z]{4,}\b", script_body))
    if devanagari > 80 and latin_words >= 25:
        v.warnings.append(
            f"Script may be too Roman-heavy ({latin_words} long English words). "
            "FULL SCRIPT should be Devanagari — Rule 2e"
        )

    v.score = min(score, v.max_score)
    if v.score < 60 and v.passed:
        v.warnings.append(f"Retention quality score low: {v.score}/100")

    return v
