"""Build and merge deep_hooks.md — one entry per transcript video_id."""
from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from lib.creator_profiles import CREATOR_CONTEXT
from lib.pattern_analyzer import analyze_single_video
from lib.paths import DATA_DIR, PATTERN_DIR

ENTRY_HEADER = re.compile(
    r"^##\s*#(\d+)\s*\|\s*([^\s|]+)\s*\|\s*GENRE:\s*(.+)$",
    re.M | re.I,
)

HOOK_MAP = {
    "question": "QUESTION_HOOK",
    "statement": "VIRAL_FACT",
    "shock_number": "SHOCK_STAT",
    "imagination": "ANALOGY_HOOK",
    "direct_address": "IDENTITY_HOOK",
    "general_statement": "NEWS_ANCHOR",
}


@dataclass
class TranscriptItem:
    video_id: str
    title: str
    path: str


def load_transcripts(creator: str) -> list[TranscriptItem]:
    creator_dir = DATA_DIR / creator
    if not creator_dir.exists():
        return []
    items: list[TranscriptItem] = []
    for video_dir in sorted(creator_dir.iterdir()):
        if not video_dir.is_dir() or video_dir.name.startswith(("_", ".")):
            continue
        tpath = video_dir / "transcript.txt"
        if not tpath.exists():
            continue
        if len(tpath.read_text(encoding="utf-8", errors="ignore").strip()) < 50:
            continue
        title = video_dir.name
        meta = video_dir / "metadata.json"
        if meta.exists():
            try:
                title = json.loads(meta.read_text(encoding="utf-8")).get("title", title)
            except json.JSONDecodeError:
                pass
        items.append(TranscriptItem(video_dir.name, title, str(tpath)))
    return items


def parse_covered_video_ids(content: str) -> set[str]:
    """Valid YouTube id-like tokens only (11 chars typical)."""
    ids: set[str] = set()
    for m in ENTRY_HEADER.finditer(content):
        vid = m.group(2).strip()
        if re.match(r"^[\w-]{8,15}$", vid) and " " not in vid and "(" not in vid:
            ids.add(vid)
    return ids


def infer_genre(title: str, hook_text: str, creator: str) -> str:
    blob = f"{title} {hook_text}".lower()
    rules = [
        (r"ipo|stock|share|mutual|sip|invest|market|crore|profit", "Finance / Markets"),
        (r"election|modi|bjp|congress|vote|sansad|politic|govt|sarkar", "Politics / Policy"),
        (r"temple|mandir|devbhoomi|spiritual|darshan|puja", "Heritage / Spiritual"),
        (r"startup|founder|ceo|company|brand|business", "Business / Startup"),
        (r"cricket|ipl|sport|match|player", "Sports"),
        (r"science|tech|ai|phone|apple|tesla", "Tech / Science"),
        (r"women|gender|safety|rights", "Social / Rights"),
        (r"travel|trip|hotel", "Travel"),
        (r"psycholog|mind|habit|focus|relationship", "Psychology / Self-help"),
    ]
    for pat, genre in rules:
        if re.search(pat, blob):
            return genre
    if "GenZway" in creator or "openletter" in creator.lower():
        return "Business Expose"
    if "Shivanshu" in creator:
        return "Documentary Explainer"
    if "KKCreate" in creator or "Prabhjot" in creator:
        return "Current Affairs"
    return "General Explainer"


def mechanical_analysis(item: TranscriptItem) -> dict:
    return analyze_single_video(item.video_id, item.path)


def format_entry(index: int, item: TranscriptItem, analysis: dict, creator: str) -> str:
    hook = analysis.get("hook", {})
    closing = analysis.get("closing", {})
    hook_text = hook.get("text", "").strip()
    hook_type = HOOK_MAP.get(hook.get("type", ""), "VIRAL_FACT")
    genre = infer_genre(item.title, hook_text, creator)
    wps = analysis.get("wps", 0)
    pacing = "RAPID" if wps >= 3.2 else "MEDIUM" if wps >= 2.5 else "SLOW"
    audience = ", ".join(analysis.get("audience_addressing", [])[:3])
    structure = analysis.get("structure", "standard_short")
    bigrams = analysis.get("top_bigrams", [])[:5]
    tics = ", ".join(f'"{b["phrase"]}"' for b in bigrams if b.get("phrase"))

    narrative = f"HOOK → BUILD ({structure.replace('_', ' ')}) → CLOSE"
    if hook_type == "QUESTION_HOOK":
        narrative = "QUESTION → CONTEXT → ANSWER/EVIDENCE → CLOSE"
    elif hook_type == "SHOCK_STAT":
        narrative = "SHOCK STAT → MECHANISM → DATA STACK → IMPLICATION → CLOSE"

    template = (
        f'"[{hook_text[:80]}...]" → [middle beats with specific fact] → [close style from this creator]'
    )
    if len(hook_text) < 100:
        template = f'"{hook_text}" → [2-3 fact beats] → [creator CTA or punchline]'

    return f"""## #{index} | {item.video_id} | GENRE: {genre}

**Title:** {item.title[:120]}
**HOOK TYPE:** {hook_type}
**EXACT HOOK (verbatim):** "{hook_text}"
**WHY IT WORKS:** Opens with {hook_type.replace('_', ' ').lower()} — stops scroll via curiosity or shock.
**NARRATIVE PATTERN:** {narrative}
**SIGNATURE TICS USED:** {tics or audience or 'see top_words in patterns/'}
**PACING:** {pacing} (~{wps} WPS)
**CTA STYLE:** {closing.get('type', 'none')} — "{closing.get('text', '')[:120]}"
**TEMPLATE EXTRACT:** {template}
"""


def build_master_sections(creator: str, entries_md: list[str]) -> str:
    hook_types: Counter[str] = Counter()
    genres: Counter[str] = Counter()
    for block in entries_md:
        m = re.search(r"\*\*HOOK TYPE:\*\*\s*(\S+)", block)
        if m:
            hook_types[m.group(1)] += 1
        m2 = re.search(r"GENRE:\s*(.+)$", block, re.M)
        if m2:
            genres[m2.group(1).strip()] += 1

    lines = [
        f"\n# MASTER HOOK LIBRARY FOR {creator}",
        "",
        "| Hook Type | Count | Share |",
        "|-----------|-------|-------|",
    ]
    total = sum(hook_types.values()) or 1
    for ht, cnt in hook_types.most_common(12):
        lines.append(f"| {ht} | {cnt} | {cnt/total*100:.0f}% |")

    lines += ["", "# GENRE MAP", "", "| Genre | Count |", "|-------|-------|"]
    for g, cnt in genres.most_common(10):
        lines.append(f"| {g} | {cnt} |")

    lines += [
        "",
        "# POWER PATTERNS (aggregated)",
        "",
        "1. **Hook → stacked facts → close** — dominant in news/explainer shorts",
        "2. **Question or shock open** — retention in first 3 seconds",
        "3. **Creator-specific CTA** — see CREATOR_MIND.md for exact phrases",
        "",
        f"# FORBIDDEN / SIGNATURE",
        "",
        f"See `creator_pattern/{creator}/CREATOR_MIND.md` for NEVER rules and mandatory vocabulary.",
        "",
    ]
    return "\n".join(lines)


def build_deep_hooks_file(
    creator: str,
    *,
    missing_only: bool = True,
) -> tuple[Path, int, int]:
    """
    Rebuild deep_hooks.md with one mechanical entry per transcript.
    Returns (path, total_transcripts, new_entries_written).
    """
    transcripts = load_transcripts(creator)
    out_dir = PATTERN_DIR / creator
    out_dir.mkdir(parents=True, exist_ok=True)
    hook_file = out_dir / "deep_hooks.md"

    existing_content = hook_file.read_text(encoding="utf-8") if hook_file.exists() else ""
    covered = parse_covered_video_ids(existing_content)

    to_process = [
        t for t in transcripts if t.video_id not in covered
    ] if missing_only else list(transcripts)

    # Parse keep existing valid entries from old file
    kept_blocks: list[str] = []
    if existing_content and missing_only:
        parts = re.split(r"(?=^## #\d+ \|)", existing_content, flags=re.M)
        for part in parts:
            if not part.strip().startswith("## #"):
                continue
            m = ENTRY_HEADER.match(part.strip().split("\n")[0])
            if m and m.group(2) in covered:
                kept_blocks.append(part.strip())

    new_blocks: list[str] = []
    start_idx = len(kept_blocks) + 1
    for i, item in enumerate(to_process, start=start_idx):
        analysis = mechanical_analysis(item)
        if analysis.get("error"):
            continue
        new_blocks.append(format_entry(i, item, analysis, creator))

    all_blocks = kept_blocks + new_blocks
    # Renumber sequentially
    renumbered: list[str] = []
    for i, block in enumerate(all_blocks, 1):
        block = re.sub(
            r"^## #\d+ \|",
            f"## #{i} |",
            block,
            count=1,
            flags=re.M,
        )
        renumbered.append(block)

    header = f"""# DEEP HOOK LIBRARY: {creator}
**Total Transcripts on disk:** {len(transcripts)}
**Per-video entries in this file:** {len(renumbered)}
**Builder:** mechanical (pattern_analyzer) — run `deep_hook_learn.py --llm` to enrich with Claude
**Creator Context:** {CREATOR_CONTEXT.get(creator, 'N/A')}

{'='*60}

## PER-TRANSCRIPT HOOK ANALYSIS (one entry per video_id)

"""

    body = "\n\n---\n\n".join(renumbered)
    master = build_master_sections(creator, renumbered)
    full = header + body + master
    hook_file.write_text(full, encoding="utf-8")
    return hook_file, len(transcripts), len(new_blocks)
