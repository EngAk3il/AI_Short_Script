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
TIMESTAMP_LINE = re.compile(r"\[\d{2}:\d{2}\]")

# Rule 2h — minimum ~2 minutes spoken
MIN_SCRIPT_WORDS = 360
MIN_SCRIPT_WORDS_SLOW = 320  # KKCreate, NehaGupta, hellooipsita
SLOW_WPS_CREATORS = frozenset({"KKCreate", "NehaGupta", "hellooipsita"})
MIN_LAST_TIMESTAMP_SEC = 115  # [01:55]
MIN_TIMESTAMP_BEATS = 12
PREFERRED_TIMESTAMP_BEATS = 14


def _extract_script_body(markdown: str) -> str:
    if "## FULL SCRIPT" in markdown:
        return markdown.split("## FULL SCRIPT", 1)[-1].split("###", 1)[0]
    if "## SCRIPT" in markdown:
        return markdown.split("## SCRIPT", 1)[-1].split("###", 1)[0]
    return markdown


def _spoken_word_count(script_body: str) -> int:
    lines = []
    for line in script_body.splitlines():
        if TIMESTAMP_LINE.search(line):
            lines.append(TIMESTAMP_LINE.sub("", line).strip())
    text = " ".join(lines) if lines else script_body
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    return len(re.findall(r"[\w\u0900-\u097F]+", text, re.UNICODE))


def _last_timestamp_seconds(script_body: str) -> int | None:
    stamps = re.findall(r"\[(\d{2}):(\d{2})\]", script_body)
    if not stamps:
        return None
    return max(int(m) * 60 + int(s) for m, s in stamps)


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
    script_body = _extract_script_body(markdown)

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
    timestamp_markers = len(TIMESTAMP_LINE.findall(script_body)) or len(
        re.findall(r"\[00:\d{2}\]|0:\d{2}\s*to|0:\d{2}\s*—", markdown)
    )
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
            r"जब|मतलब|इसीलिए|लेकिन|तो\s+लगता|ने\s+देखा|इस\s+तरह\s+से|सरप्राइज़|"
            r"\bjab\b|\bmatlab\b|\blekin\b|\bisliye\b|\balso\b|is tarah se|surprise",
            script_body,
            re.I,
        )
    )
    money_stat_lines = len(
        re.findall(
            r"^\[\d{2}:\d{2}\].*(?:₹|Rs\.?|\$|\d+\s*करोड़|\d+\s*लाख)",
            script_body,
            re.I | re.M,
        )
    )
    if money_stat_lines >= 3 and teaching_markers < 2:
        v.warnings.append(
            "Possible headline stack: many ₹/stat lines but few teaching connectors "
            "(जब/मतलब/लेकिन/इसीलिए). Teach one chain — see SCRIPT_RULES.md Rule 2f"
        )

    # Rule 2h — minimum 2-minute script
    spoken_words = _spoken_word_count(script_body)
    min_words = (
        MIN_SCRIPT_WORDS_SLOW if creator in SLOW_WPS_CREATORS else MIN_SCRIPT_WORDS
    )
    if spoken_words and spoken_words < min_words:
        v.passed = False
        v.errors.append(
            f"Script too short for 2-min target: {spoken_words} spoken words "
            f"(need ≥{min_words}). See SCRIPT_RULES.md Rule 2h"
        )
    elif spoken_words and spoken_words < min_words + 20:
        v.warnings.append(
            f"Script borderline short ({spoken_words} words; target ≥{min_words} for ~2:00)"
        )

    last_ts = _last_timestamp_seconds(script_body)
    if last_ts is not None and last_ts < MIN_LAST_TIMESTAMP_SEC:
        v.passed = False
        v.errors.append(
            f"Last timestamp [{last_ts // 60:02d}:{last_ts % 60:02d}] is under 2 minutes "
            f"(need ≥[01:55]). See SCRIPT_RULES.md Rule 2h"
        )
    if timestamp_markers < MIN_TIMESTAMP_BEATS:
        v.passed = False
        v.errors.append(
            f"Need ≥{MIN_TIMESTAMP_BEATS} `[00:00]` beats for 2-min script; "
            f"found {timestamp_markers}"
        )
    elif timestamp_markers < PREFERRED_TIMESTAMP_BEATS:
        v.warnings.append(
            f"Prefer ≥{PREFERRED_TIMESTAMP_BEATS} beats for explainers; found {timestamp_markers}"
        )

    # Rule 2e — Romanized Hinglish default (not pure Devanagari)
    devanagari = len(re.findall(r"[\u0900-\u097F]", script_body))
    latin_words = len(re.findall(r"\b[a-zA-Z]{3,}\b", script_body))
    if devanagari > 180 and latin_words < 50:
        v.passed = False
        v.errors.append(
            "FULL SCRIPT is mostly Devanagari — use Romanized Hinglish (Latin letters). "
            "See SCRIPT_RULES.md Rule 2e"
        )

    v.score = min(score, v.max_score)
    if v.score < 60 and v.passed:
        v.warnings.append(f"Retention quality score low: {v.score}/100")

    return v
