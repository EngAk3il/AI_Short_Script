"""Analyze ingested transcripts — date density, openers, rhythm — for agents."""

from __future__ import annotations

import json
import re
from pathlib import Path

from lib.paths import DATA_DIR

DATE_IN_SPEECH = re.compile(
    r"\b20\d{2}\b|"
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b|"
    r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b|"
    r"मई|जनवरी|फरवरी|मार्च|अप्रैल|जून|जुलाई|अगस्त|सितंबर|अक्टूबर|नवंबर|दिसंबर|"
    r"\d{1,2}\s+(may|march|january)",
    re.I,
)

SEGMENT = re.compile(r"\[(\d{2}:\d{2})\]\s*(.+)")


def analyze_transcript_text(text: str) -> dict:
    """Return voice metrics agents must mirror."""
    segments = SEGMENT.findall(text)
    bodies = [b.strip() for _, b in segments] if segments else [text.strip()]
    words_per_seg = []
    for b in bodies:
        w = len(re.findall(r"\S+", b))
        if w:
            words_per_seg.append(w)

    full = " ".join(bodies)
    low = full.lower()

    signatures: dict[str, bool] = {
        "doston": "दोस्तों" in full or "doston" in low,
        "aakhir_kya": bool(re.search(r"aakhir kya", low)),
        "kya_aap_jaante": bool(re.search(r"kya aap jaante", low)),
        "seedha_matlab": bool(re.search(r"seedha matlab", low)),
        "dar_asal": bool(re.search(r"dar[- ]?asal|दर[- ]?असल", low)),
        "aaiye_samajhte": bool(re.search(r"aaiye samajhte", low)),
        "simple_words": bool(re.search(r"simple words|simple samjho", low)),
        "devbhoomi": "devbhoomi" in low or "देवभूमि" in full,
        "darshan": "darshan" in low or "दर्शन" in full,
        "lekin": " lekin " in f" {low} " or full.startswith("लेकिन"),
    }

    return {
        "segment_count": len(bodies),
        "date_mentions_in_speech": len(DATE_IN_SPEECH.findall(full)),
        "avg_words_per_segment": round(sum(words_per_seg) / len(words_per_seg), 1)
        if words_per_seg
        else 0,
        "opening_line": bodies[0][:120] if bodies else "",
        "signatures_found": [k for k, v in signatures.items() if v],
        "uses_timestamps": bool(segments),
    }


def find_best_transcript_for_topic(creator: str, topic: str, limit: int = 1) -> list[tuple[str, str, dict]]:
    """Score all transcripts by topic word overlap; return (video_id, text, analysis)."""
    creator_dir = DATA_DIR / creator
    if not creator_dir.exists():
        return []

    topic_words = set(re.findall(r"[a-zA-Z\u0900-\u097F]{3,}", topic.lower()))
    scored: list[tuple[int, str, str, dict]] = []

    for video_dir in creator_dir.iterdir():
        if not video_dir.is_dir() or video_dir.name.startswith("_"):
            continue
        t_path = video_dir / "transcript.txt"
        if not t_path.exists():
            continue
        text = t_path.read_text(encoding="utf-8", errors="ignore").strip()
        if len(text) < 80:
            continue

        blob = text.lower()
        meta_path = video_dir / "metadata.json"
        title = ""
        if meta_path.exists():
            try:
                title = json.loads(meta_path.read_text()).get("title", "").lower()
            except json.JSONDecodeError:
                pass

        score = sum(2 for w in topic_words if w in blob)
        score += sum(3 for w in topic_words if w in title)
        if score > 0:
            scored.append((score, video_dir.name, text, analyze_transcript_text(text)))

    scored.sort(key=lambda x: -x[0])
    return [(vid, txt, ana) for _, vid, txt, ana in scored[:limit]]


def format_analysis_block(video_id: str, title: str, text: str, analysis: dict) -> str:
    """Agent-facing: what to copy vs avoid."""
    date_n = analysis["date_mentions_in_speech"]
    date_rule = (
        "**Dates in speech:** NONE in reference — do **not** repeat '14 May 2026' in every line. "
        "At most **one** date in the full script if essential; prefer 'abhi', 'is hafte', 'court ne order diya'."
        if date_n == 0
        else f"**Dates in speech:** reference uses ~{date_n} — match that density only."
    )

    sigs = ", ".join(analysis["signatures_found"]) or "(none detected — use CREATOR_MIND)"
    excerpt = text.strip()[:2200]

    return f"""### Reference transcript: `{video_id}` — {title}

{date_rule}
**Segments:** {analysis['segment_count']} · **~{analysis['avg_words_per_segment']} words/segment** (match this length)
**Opening (copy rhythm, not topic):** "{analysis['opening_line'][:100]}..."
**Phrases present in reference:** {sigs}

```
{excerpt}
```
"""
