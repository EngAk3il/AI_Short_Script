"""Pick per-topic script structure from real ingested transcripts — not one table for all."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from lib.paths import DATA_DIR
from lib.script_formats import OUTPUT_FORMAT

# Archetypes learned from data/<creator>/*/transcript.txt + deep_hooks NARRATIVE PATTERN
ARCHETYPES: dict[str, dict[str, dict]] = {
    "NiharikaChoudhary": {
        "legal_explainer": {
            "keywords": [
                "court", "sc ", "supreme", "law", "legal", "rape", "sentence", "bail",
                "unnao", "sengar", "rights", "constitutional", "hc ", "high court",
            ],
            "reference_video": "8EEqmu6MVwY",
            "reference_title": "Electoral bonds / SC legal explainer rhythm",
            "pattern": "HOOK → BUILD (micro punch) → CLOSE",
            "structure": """Use **ingested timestamp prose only** (no markdown table):
```
[00:00] Shock ruling or term + court action in one breath.
[00:08] `Aakhir kya tha` — unpack what the order actually means in plain Hindi.
[00:15] Civic stake — `aap khud sochiye` / accountability / victim voice.
[00:22] One fact beat (date, who must be heard, what happens next).
[00:30] `Simple words mein` — one-line takeaway for the viewer.
[00:38] Opinion CTA — `Aap kya sochte hain?` + comment / follow journalist.
```""",
        },
        "question_evidence": {
            "keywords": [
                "scam", "bank", "idfc", "kharge", "fuel", "petrol", "modi", "crisis",
                "economic", "hike", "political", "government", "explained",
            ],
            "reference_video": "7FHRhFFa28I",
            "reference_title": "IDFC scam — Aakhir kya hua question chain",
            "pattern": "QUESTION → CONTEXT → ANSWER/EVIDENCE → CLOSE",
            "structure": """Use **ingested timestamp prose** (no table):
```
[00:00] `!` headline shock OR `Aakhir kya hua?` on the news event.
[00:06] What happened — one concrete fact (Rs, date, who said what).
[00:12] `Lekin` — second layer (why opposition/government framing differs).
[00:18] Wallet or citizen impact in simple Hindi.
[00:26] `Simple words mein` / `Seedha matlab` — what changes for aap.
[00:34] Balanced line (both narratives) without partisan cheerleading.
[00:42] `Aap kya sochte hain?` comment CTA.
```""",
        },
        "inspirational_bio": {
            "keywords": [
                "satheesan", "cm ", "kerala", "commander", "biography", "inspiration",
                "leader", "oath", "congress", "race", "story",
            ],
            "reference_video": "yLg0odaDIiM",
            "reference_title": "Human arc / political biography beats",
            "pattern": "HOOK → BUILD (detailed explainer) → CLOSE",
            "structure": """Use **ingested timestamp prose** (no table):
```
[00:00] Name + win + nickname hook in one line.
[00:08] `Aakhir kya hua` — internal party fight / factions in plain words.
[00:16] Timeline beat (swearing-in date, venue) — specific, not vague.
[00:24] Human arc — organisation person vs celebrity; what changes as CM.
[00:32] `Simple words mein` — why nickname matters for governance test.
[00:40] Open question CTA — inspire or challenge, not attack.
```""",
        },
    },
    "TheInformedCitizen": {
        "geo_domino": {
            "keywords": [
                "hormuz", "oil", "route", "map", "3d", "uae", "fujairah", "energy",
                "strait", "pipeline", "geography", "port", "bypass", "modi tour",
            ],
            "reference_video": "FO2JWEO1BrQ",
            "reference_title": "Mount Kailash — long domino build + map facts",
            "pattern": "HOOK → BUILD (detailed explainer) → CLOSE",
            "structure": """Use **flowing [00:00] timestamp prose** — NOT Shivanshu 4-column table:
```
[00:00] Open with place/route mystery or blocked chokepoint; say you will map it.
[00:07] Fact layer 1 (geography / port / why Hormuz matters) — `VISUAL: 3D map`.
[00:15] `Lekin` pivot — alternate route (e.g. Fujairah) step by step on map.
[00:23] Fact layer 2 (LPG, strategic reserves, tour context).
[00:31] `Dar-asal` or `लेकिन असलियत में` — what this means for India's supply.
[00:39] `Aaiye samajhte hain` — chain: blockade → route → storage → price risk.
[00:47] `Seedha matlab aapke liye` — petrol/LPG/inflation link.
[00:55] Soft subscribe — informative / map explainers.
```""",
        },
        "geo_punch": {
            "keywords": [
                "heat", "heatwave", "rain", "imd", "monsoon", "climate", "weather",
                "rajasthan", "barmer", "split", "flood", "lou", "temperature",
            ],
            "reference_video": "ldNmNRVPlkc",
            "reference_title": "Aravalli — headline punch + environmental stakes",
            "pattern": "HOOK → BUILD (micro punch) → CLOSE",
            "structure": """Use **short punch open + timestamp prose**:
```
[00:00] `!` or shocking headline — split India / two climates at once.
[00:06] Name regions on map — west heat belt vs NE/south rain belt.
[00:12] One IMD-style fact (above-normal heatwave days / heavy rain alert).
[00:18] `VISUAL: map` — colour west red, east blue; pin Barmer or sample city.
[00:24] `Lekin` — monsoon onset nuance (Andaman / early June relief).
[00:30] `Seedha matlab aapke liye` — what to do in your state.
[00:38] Share + subscribe for map Shorts.
```""",
        },
        "defense_chain": {
            "keywords": [
                "agni", "missile", "mirv", "divyastra", "defence", "defense", "warhead",
                "rajnath", "strategic", "china", "pakistan", "test", "odisha",
            ],
            "reference_video": "MYvS4pE9iIU",
            "reference_title": "Arctic / strategic — domino escalation chain",
            "pattern": "HOOK → BUILD (detailed explainer) → CLOSE",
            "structure": """Use **domino-chain timestamp prose** (like geo-war explainers):
```
[00:00] Test headline + range shock; promise to decode tech in plain Hindi.
[00:08] What MIRV is — one missile, multiple independent targets.
[00:16] Test facts: date, Odisha, Indian Ocean impacts — `VISUAL: trajectory map`.
[00:24] Minister/strategic quote beat — capability, not chest-thumping only.
[00:32] `Aaiye samajhte hain` — deterrence vs daily life for citizen.
[00:40] Regional angle (credible reach) without warmongering.
[00:48] `Seedha matlab` + informative subscribe CTA.
```""",
        },
    },
    "NehaGupta": {
        "temple_list": {
            "keywords": [
                "jatra", "devotee", "mandir", "temple", "festival", "mahotsav", "darshan",
                "karnataka", "huligemma", "pilgrim", "bhakt", "seva", "meal",
            ],
            "reference_video": "hxWwtztLxLY",
            "reference_title": "Devbhoomi temple list + Jai Mata Di close",
            "pattern": "HOOK → BUILD (standard short) → CLOSE",
            "structure": """Use **Neha's real [00:00] list rhythm** — NOT news tables, NOT Shivanshu director blocks unless paired with timestamps:
```
[00:00] Place + festival name — scale hook (lakhs/crore footfall).
[00:05] Beat 1 — dates + what happens (Maharathotsava / peak day).
[00:12] Beat 2 — Mahadasoha / free meals / seva detail.
[00:19] Beat 3 — why it matters spiritually (`darshan`, `hamari sanskriti`).
[00:26] Visual line — crowd, chariot, kitchen (for editor).
[00:32] Pride line — `garv` / heritage, not politics.
[00:38] `Comment mein 'जय माता' likhein` or topic-specific comment ask.
```""",
        },
        "heritage_mystery": {
            "keywords": [
                "oath", "ceremony", "astrology", "pandal", "stadium", "kerala", "satheesan",
                "swearing", "muhurat", "sacred", "ritual", "shapath",
            ],
            "reference_video": "qp_ptIZBdy0",
            "reference_title": "Kya aap jaante hain — cultural discovery",
            "pattern": "QUESTION → CONTEXT → ANSWER/EVIDENCE → CLOSE",
            "structure": """Use **क्या आप जानते हैं open + timestamp beats**:
```
[00:00] `Kya aap jaante hain` — ceremony fact that sounds unbelievable?
[00:05] Venue + scale (3000-seat pandal, Central Stadium).
[00:12] Date + political moment framed as ritual, not debate.
[00:19] Astrology / muhurat angle — curious tone, not mockery.
[00:25] `Hamari sanskriti` — faith + public life blend.
[00:32] `Darshan` moment language for the crowd/ritual feel.
[00:38] Comment CTA — place name or 'Kerala'.
```""",
        },
        "diaspora_pride": {
            "keywords": [
                "uae", "diaspora", "indian", "million", "expat", "soft power", "investment",
                "modi visit", "abroad", "global", "pride", "dubai",
            ],
            "reference_video": "qp_ptIZBdy0",
            "reference_title": "Regional pride list — adapt to diaspora facts",
            "pattern": "QUESTION → CONTEXT → ANSWER/EVIDENCE → CLOSE",
            "structure": """Use **discovery question + numbered pride beats**:
```
[00:00] `Kya aap jaante hain` — how many Indians live in UAE?
[00:05] Number + Modi visit news peg (May 2026).
[00:12] Investment / energy partnership fact (one stat, sourced).
[00:19] Who diaspora is — doctors, nurses, engineers as ambassadors.
[00:25] `Hamari sanskriti` abroad — temples, festivals, community.
[00:32] `Garv` + humble line (don't boast, celebrate).
[00:38] `Comment mein 'UAE' likhein` if family is there.
```""",
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
    excerpt: str = ""


def _topic_blob(topic: str) -> str:
    return topic.lower()


def pick_archetype(creator: str, topic: str) -> TranscriptArchetype:
    """Score topic keywords against archetypes; return best match with transcript excerpt."""
    blob = _topic_blob(topic)
    catalog = ARCHETYPES.get(creator, {})
    if not catalog:
        return TranscriptArchetype(
            key="default",
            creator=creator,
            pattern="HOOK → BUILD → CLOSE",
            reference_video="",
            reference_title="(no archetype catalog)",
            structure=OUTPUT_FORMAT.get(creator, "- Use [00:00] timestamp prose from samples."),
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
    vid = spec["reference_video"]
    excerpt = _load_transcript_excerpt(creator, vid, max_chars=1800)

    return TranscriptArchetype(
        key=best_key,
        creator=creator,
        pattern=spec["pattern"],
        reference_video=vid,
        reference_title=spec["reference_title"],
        structure=spec["structure"],
        excerpt=excerpt,
    )


def _load_transcript_excerpt(creator: str, video_id: str, max_chars: int = 1800) -> str:
    path = DATA_DIR / creator / video_id / "transcript.txt"
    if not path.exists():
        return "(transcript not found — use structure template above)"
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    meta_path = DATA_DIR / creator / video_id / "metadata.json"
    title = video_id
    if meta_path.exists():
        try:
            title = json.loads(meta_path.read_text()).get("title", title)
        except json.JSONDecodeError:
            pass
    return f"**[Reference: {video_id} | {title}]**\n```\n{text[:max_chars]}\n```"


def format_instructions_for_bundle(creator: str, topic: str) -> str:
    """Block injected into *_context.md — agents must follow this, not generic table."""
    arch = pick_archetype(creator, topic)
    lines = [
        "\n## REQUIRED FORMAT (from real transcript — NOT a generic table)\n",
        f"**Matched archetype:** `{arch.key}`",
        f"**Narrative pattern:** {arch.pattern}",
        f"**Copy structure from:** {arch.reference_title} (`{arch.reference_video}`)",
        "",
        arch.structure,
        "",
        "### Reference transcript excerpt (mirror line length & connectors)\n",
        arch.excerpt,
        "",
        "**Rules:**",
        "- Write the script body in the same shape as the excerpt (usually `[00:00]` lines).",
        "- Do NOT use another creator's table format (e.g. Shivanshu 4-column) unless excerpt shows it.",
        "- Name the matched `reference_video` in your DNA Adherence Audit.",
    ]
    return "\n".join(lines)

