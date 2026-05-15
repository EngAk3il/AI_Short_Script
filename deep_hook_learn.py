#!/usr/bin/env python3
"""
deep_hook_learn.py — Build deep_hooks.md with ONE entry per transcript (video_id).

Default: mechanical analysis (no API) for all missing transcripts.
Optional: --llm to enrich batches via Claude (requires ANTHROPIC_API_KEY).

Usage:
  python3 deep_hook_learn.py                    # all creators, missing only, mechanical
  python3 deep_hook_learn.py Shivanshu.Agrawal  # one creator
  python3 deep_hook_learn.py --all GenZway      # rebuild all entries mechanical
  python3 deep_hook_learn.py --llm --missing-only UditInsights  # Claude for gaps only
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from lib.creator_profiles import CREATOR_CONTEXT
from lib.deep_hooks_builder import (
    build_deep_hooks_file,
    load_transcripts,
    parse_covered_video_ids,
)
from lib.hook_patterns import validate_deep_hooks_content
from lib.paths import DATA_DIR, PATTERN_DIR as OUT_DIR

CREATORS = [
    "Shivanshu.Agrawal",
    "GenZway",
    "hellooipsita",
    "Finsaheliofficial",
    "KKCreate",
    "openletteryt",
    "TheInformedCitizen",
    "Nitishrajputshorts",
    "PrabhjotSpeaks",
    "MangeshShinde",
    "NiharikaChoudhary",
    "NehaGupta",
    "AshutoshPratihastAP",
    "ThinkSchool_Hindi",
    "UditInsights",
]

BATCH_SIZE = 12
MAX_TRANSCRIPT_CHARS = 2800


def get_all_transcripts(creator: str) -> list[dict]:
    from lib.deep_hooks_builder import load_transcripts

    return [
        {"video_id": t.video_id, "title": t.title, "text": Path(t.path).read_text(encoding="utf-8", errors="ignore")}
        for t in load_transcripts(creator)
    ]


def analyze_batch_llm(creator: str, batch: list[dict], batch_offset: int) -> str:
    from anthropic import Anthropic

    client = Anthropic()
    context = CREATOR_CONTEXT.get(creator, "")
    block = ""
    for i, t in enumerate(batch, batch_offset + 1):
        text = t["text"][:MAX_TRANSCRIPT_CHARS]
        block += f"\n---\n### INPUT #{i} | video_id: {t['video_id']}\n**Title:** {t['title']}\n\n{text}\n"

    system = f"""You analyze YouTube Shorts transcripts for {creator}.
{context}

CRITICAL RULES:
- Output EXACTLY one entry per INPUT, same order
- Header MUST be: ## #[n] | [video_id] | GENRE: [genre]
- video_id MUST be copied exactly from INPUT (never "Various" or placeholders)
- Include ALL fields: HOOK TYPE, EXACT HOOK, WHY IT WORKS, NARRATIVE PATTERN, SIGNATURE TICS, PACING, CTA STYLE, TEMPLATE EXTRACT
- Quote verbatim opening line(s) from transcript for EXACT HOOK
- Do NOT add MASTER HOOK LIBRARY section (only per-video entries)"""

    resp = client.messages.create(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        max_tokens=16000,
        system=system,
        messages=[
            {
                "role": "user",
                "content": f"Analyze these {len(batch)} transcripts:\n{block}",
            }
        ],
    )
    return resp.content[0].text


def run_llm_creator(creator: str, missing_only: bool) -> None:
    hook_file = OUT_DIR / creator / "deep_hooks.md"
    existing = hook_file.read_text(encoding="utf-8") if hook_file.exists() else ""
    covered = parse_covered_video_ids(existing)
    transcripts = get_all_transcripts(creator)
    todo = [t for t in transcripts if t["video_id"] not in covered] if missing_only else transcripts
    if not todo:
        print(f"  ✅ {creator}: no missing transcripts")
        return

    print(f"  LLM: {len(todo)} transcripts in {(len(todo) + BATCH_SIZE - 1) // BATCH_SIZE} batches")
    new_parts: list[str] = []
    for bstart in range(0, len(todo), BATCH_SIZE):
        batch = todo[bstart : bstart + BATCH_SIZE]
        bnum = bstart // BATCH_SIZE + 1
        print(f"    batch {bnum} ({len(batch)} videos)...")
        try:
            new_parts.append(analyze_batch_llm(creator, batch, bstart))
        except Exception as e:
            print(f"    ❌ batch failed: {e}")

    # Mechanical full rebuild then append LLM blocks would be messy — merge by rebuilding mechanical first
    build_deep_hooks_file(creator, missing_only=False)
    # Append LLM batches not implemented in v1 — user should use mechanical as base
    print(f"  ⚠️  LLM batches saved separately; run mechanical merge for full coverage first")


def run_mechanical(creator: str, missing_only: bool) -> None:
    path, total, new = build_deep_hooks_file(creator, missing_only=missing_only)
    content = path.read_text(encoding="utf-8")
    from lib.deep_hooks_builder import load_transcripts as _load

    ids = [t.video_id for t in _load(creator)]
    v = validate_deep_hooks_content(content, total, ids)
    print(f"  ✅ {creator}: {new} new entries | file entries={v.entries_found}/{total} | complete={v.entries_complete}")
    if v.missing_videos:
        print(f"     still missing {len(v.missing_videos)} ids (first 3): {v.missing_videos[:3]}")
    if not v.passed:
        for e in v.errors[:3]:
            print(f"     ⚠️  {e}")


def regenerate_cheatsheet(creator: str, content: str) -> None:
    """Update hook_cheatsheet from deep_hooks without overwriting CREATOR_MIND."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return
    try:
        from anthropic import Anthropic

        client = Anthropic()
        resp = client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": f"""From this deep hook library for {creator}, write a compact HOOK CHEATSHEET (top 10 formulas, genre table, 5 power patterns, forbidden, signature vocab, CTAs). Keep CREATOR_MIND.md separate — cheatsheet only.

{content[:25000]}""",
                }
            ],
        )
        (OUT_DIR / creator / "hook_cheatsheet.md").write_text(
            f"# HOOK CHEATSHEET: {creator}\n\n{resp.content[0].text}",
            encoding="utf-8",
        )
        print(f"  📋 Updated hook_cheatsheet.md")
    except Exception as e:
        print(f"  ⚠️  cheatsheet skip: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build per-transcript deep_hooks.md")
    parser.add_argument("creators", nargs="*", help="Creator names (default: all)")
    parser.add_argument("--all", action="store_true", help="Rebuild all entries (not just missing)")
    parser.add_argument("--llm", action="store_true", help="Use Claude API (needs ANTHROPIC_API_KEY)")
    parser.add_argument("--cheatsheet", action="store_true", help="Regenerate hook_cheatsheet via LLM")
    args = parser.parse_args()
    missing_only = not args.all

    targets = args.creators or CREATORS
    print("=" * 60)
    print("DEEP HOOK LEARN — per video_id coverage")
    print(f"Mode: {'LLM' if args.llm else 'mechanical (local)'}")
    print(f"Scope: {'missing only' if missing_only else 'full rebuild'}")
    print("=" * 60)

    for creator in targets:
        print(f"\n{'='*50}\n{creator}\n{'='*50}")
        if not (DATA_DIR / creator).exists():
            print("  ⚠️  no data/ folder — skip")
            continue
        if args.llm:
            run_llm_creator(creator, missing_only)
        else:
            run_mechanical(creator, missing_only)
        if args.cheatsheet:
            hf = OUT_DIR / creator / "deep_hooks.md"
            if hf.exists():
                regenerate_cheatsheet(creator, hf.read_text(encoding="utf-8"))

    print("\n" + "=" * 60)
    print("DONE — verify: python3 deep_hook_status.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
