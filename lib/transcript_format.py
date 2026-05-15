"""Pick per-topic script structure from real ingested transcripts — not one table for all."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from lib.paths import DATA_DIR
from lib.script_formats import OUTPUT_FORMAT
from lib.transcript_analysis import (
    analyze_transcript_text,
    find_best_transcript_for_topic,
    format_analysis_block,
)

# Archetypes: narrative pattern hints only. Reference video resolved by topic search when possible.
ARCHETYPES: dict[str, dict[str, dict]] = {
    "NiharikaChoudhary": {
        "legal_explainer": {
            "keywords": [
                "court", "sc ", "supreme", "law", "legal", "rape", "sentence", "bail",
                "unnao", "sengar", "rights", "constitutional", "hc ", "high court",
            ],
            "fallback_video": "8EEqmu6MVwY",
            "pattern": "HOOK → BUILD (micro punch) → CLOSE",
            "structure": """Mirror reference `[00:00]` lines — **no dates in every beat** (reference has ~0 dates in speech).

1. Open: ruling/term + shock in one breath (like electoral-bonds legal Short).
2. `Aakhir kya tha` / `Aakhir kya hua` — what the order **means** for people.
3. Civic stake — victim/accountability; `Aap khud sochiye` if reference uses it.
4. One concrete legal fact (who must be heard, what was set aside) — **no calendar spam**.
5. Optional: `Simple words mein` only if explaining a legal term.
6. Close: `Aap kya sochte hain?` + comment / follow.""",
        },
        "question_evidence": {
            "keywords": [
                "scam", "bank", "idfc", "kharge", "fuel", "petrol", "modi", "crisis",
                "economic", "hike", "political", "government", "explained",
            ],
            "fallback_video": "7FHRhFFa28I",
            "pattern": "QUESTION → CONTEXT → ANSWER/EVIDENCE → CLOSE",
            "structure": """Mirror IDFC-style `Aakhir kya hua?` chain — **max 1 date in full script**.

1. Headline shock or `Aakhir kya hua?` on the event.
2. What happened — Rs / who said (one beat).
3. `Lekin` — second layer (opposition vs government framing).
4. Wallet impact in her Hindi (not wire copy).
5. Balanced line — both sides, no cheerleading.
6. `Aap kya sochte hain?`""",
        },
        "inspirational_bio": {
            "keywords": [
                "satheesan", "cm ", "kerala", "commander", "biography", "inspiration",
                "leader", "oath", "congress", "race", "story",
            ],
            "fallback_video": "wBsuIbQ2ZR8",
            "pattern": "HOOK → BUILD → CLOSE",
            "structure": """Human arc Short — question or contrast open, **not news ticker dates**.

1. Name + win + nickname.
2. `Aakhir kya hua` — internal fight in plain words.
3. What changes for state (oath venue, coalition) — one time reference OK.
4. Organisation person vs celebrity framing.
5. Open question CTA — inspire, don't attack.""",
        },
    },
    "TheInformedCitizen": {
        "geo_domino": {
            "keywords": [
                "hormuz", "oil", "route", "map", "3d", "uae", "fujairah", "energy",
                "strait", "pipeline", "geography", "port", "bypass", "modi tour",
            ],
            "fallback_video": "TsiWJSld98s",
            "pattern": "HOOK → BUILD (detailed explainer) → CLOSE",
            "structure": """**Real geo open:** `दोस्तों, [topic]...` + map layers — NOT fake `Dar-asal` unless reference has it.

1. `दोस्तों` + why this route/place matters for India.
2. Map beat 1 — chokepoint / region (editor: 3D map).
3. `Lekin` — alternate path or second fact.
4. Citizen impact — petrol/LPG/inflation link (`Seedha matlab` if natural).
5. Comment which topic next + follow (like Rajasthan geo Short).""",
        },
        "geo_punch": {
            "keywords": [
                "heat", "heatwave", "rain", "imd", "monsoon", "climate", "weather",
                "rajasthan", "barmer", "split", "flood", "lou", "temperature",
            ],
            "fallback_video": "ldNmNRVPlkc",
            "pattern": "HOOK → BUILD (micro punch) → CLOSE",
            "structure": """Aravalli-style punch headline → stakes — short segments.

1. `!` headline — two climates / one country split.
2. Name west vs east regions on map.
3. One IMD-type fact — no date in every line.
4. `Seedha matlab aapke liye` — what to do in your region.
5. Share / follow map channel.""",
        },
        "defense_chain": {
            "keywords": [
                "agni", "missile", "mirv", "divyastra", "defence", "defense",
                "warhead", "rajnath", "strategic", "china", "pakistan", "test", "odisha",
            ],
            "fallback_video": "MYvS4pE9iIU",
            "pattern": "HOOK → BUILD (detailed explainer) → CLOSE",
            "structure": """Domino escalation (Arctic-style) — long flowing Hindi, map for trajectory.

1. Test/capability headline — what changed.
2. Explain tech in plain Hindi (MIRV = one missile, many targets).
3. Strategic meaning — deterrence, not war hype.
4. `Seedha matlab aapke liye` / background line from CREATOR_MIND.
5. Soft informative subscribe if reference closes that way.""",
        },
    },
    "NehaGupta": {
        "temple_list": {
            "keywords": [
                "jatra", "devotee", "mandir", "temple", "festival", "mahotsav", "darshan",
                "karnataka", "huligemma", "pilgrim", "bhakt", "seva", "meal",
            ],
            "fallback_video": "hxWwtztLxLY",
            "pattern": "HOOK → BUILD (standard short) → CLOSE",
            "structure": """Temple/festival **list rhythm** — `Devbhoomi`/place open, **no news dates**.

1. Region + festival + scale (lakhs) — not "May 11-14, 2026" repeatedly.
2. Peak moment / Maharathotsava / crowd visual.
3. Seva / Mahadasoha / free meals.
4. `darshan` + `hamari sanskriti` pride.
5. `Comment mein 'जय माता'` or place-specific ask.""",
        },
        "heritage_mystery": {
            "keywords": [
                "oath", "ceremony", "astrology", "pandal", "stadium", "kerala", "satheesan",
                "swearing", "muhurat", "sacred", "ritual", "shapath",
            ],
            "fallback_video": "qp_ptIZBdy0",
            "pattern": "QUESTION → CONTEXT → CLOSE",
            "structure": """`Kya aap jaante hain` discovery — curious, not political debate.

1. Question hook — surprising ceremony fact.
2. Place + scale (pandal, stadium).
3. Ritual/astrology angle — respectful curiosity.
4. `hamari sanskriti` / `darshan` language.
5. Comment CTA — place name.""",
        },
        "diaspora_pride": {
            "keywords": [
                "uae", "diaspora", "indian", "million", "expat", "soft power", "investment",
                "modi visit", "abroad", "global", "pride", "dubai",
            ],
            "fallback_video": "qp_ptIZBdy0",
            "pattern": "QUESTION → CONTEXT → CLOSE",
            "structure": """Regional pride discovery — **no "May 2026" in every line**.

1. `Kya aap jaante hain` — diaspora number.
2. Who they are (doctors, nurses, engineers).
3. `hamari sanskriti` abroad.
4. `Garv` + humble tone.
5. Comment `UAE` if family there.""",
        },
    },
}


@dataclass
class TranscriptArchetype:
    key: str
    creator: str
    pattern: str
    reference_video: str
    reference_title: str
    structure: str
    analysis_block: str = ""


def pick_archetype(creator: str, topic: str) -> TranscriptArchetype:
    blob = topic.lower()
    catalog = ARCHETYPES.get(creator, {})
    if not catalog:
        return TranscriptArchetype(
            key="default",
            creator=creator,
            pattern="HOOK → BUILD → CLOSE",
            reference_video="",
            reference_title="(no archetype)",
            structure=OUTPUT_FORMAT.get(creator, "- Use [00:00] prose from samples."),
        )

    best_key = ""
    best_score = -1
    for key, spec in catalog.items():
        score = sum(1 for kw in spec["keywords"] if kw in blob)
        if score > best_score:
            best_score = score
            best_key = key

    if best_score <= 0:
        best_key = next(iter(catalog))

    spec = catalog[best_key]
    fallback = spec["fallback_video"]

    # Prefer topic-matched transcript over static fallback
    video_id = fallback
    title = spec.get("reference_title", fallback)
    text = ""
    analysis_block = ""

    topic_matches = find_best_transcript_for_topic(creator, topic, limit=1)
    if topic_matches:
        video_id, text, analysis = topic_matches[0]
        meta_path = DATA_DIR / creator / video_id / "metadata.json"
        if meta_path.exists():
            try:
                title = json.loads(meta_path.read_text()).get("title", video_id)
            except json.JSONDecodeError:
                title = video_id
        analysis_block = format_analysis_block(video_id, title, text, analysis)
    else:
        path = DATA_DIR / creator / fallback / "transcript.txt"
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="ignore")
            analysis = analyze_transcript_text(text)
            meta_path = DATA_DIR / creator / fallback / "metadata.json"
            if meta_path.exists():
                try:
                    title = json.loads(meta_path.read_text()).get("title", fallback)
                except json.JSONDecodeError:
                    pass
            analysis_block = format_analysis_block(fallback, title, text, analysis)

    return TranscriptArchetype(
        key=best_key,
        creator=creator,
        pattern=spec["pattern"],
        reference_video=video_id,
        reference_title=title,
        structure=spec["structure"],
        analysis_block=analysis_block,
    )


def format_instructions_for_bundle(creator: str, topic: str) -> str:
    arch = pick_archetype(creator, topic)
    hooks_note = (
        "Pick **EXACT HOOK** from Topic-matched hooks — adapt sentence shape, swap facts. "
        "Do NOT open like a news ticker (`14 May 2026 ko...`)."
    )
    return "\n".join(
        [
            "\n## REQUIRED FORMAT (imitate reference video — intelligence required)\n",
            f"**Matched archetype:** `{arch.key}`",
            f"**Narrative pattern:** {arch.pattern}",
            f"**Primary reference video:** `{arch.reference_video}` — {arch.reference_title}",
            "",
            "### Structure guide (beats — not a table)\n",
            arch.structure,
            "",
            hooks_note,
            "",
            arch.analysis_block or "(no transcript analysis — ingest data for this creator)",
            "",
            "### Hard rules\n",
            "- **Date density:** match reference (see analysis above). Never repeat the same date in 3+ lines.",
            "- **Phrases:** only use signature phrases **present in reference** or listed in CREATOR_MIND.",
            "- **Segment count & length:** match reference analysis.",
            "- **Devanagari** speech; hook = reference opener **shape**, not assignment headline in Roman.",
            "- **Retention:** teach ONE linked chain (or list/geo/legal per reference) — NOT a headline stack of stats.",
            "- **WATCH-THROUGH MAP:** column `Viewer question (why they stay)` required.",
            "- Read `CREATOR_SCRIPT_INTELLIGENCE.md` + `SCRIPT_RULES.md` Rule 2f–2g if unsure.",
            "- DNA audit: `Opening mimics: \"...\" → \"...\"` and confirm not headline-only.",
        ]
    )
