#!/usr/bin/env python3
"""Validate creator_pattern/<creator>/deep_hooks.md per-transcript coverage."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.generation_context import load_transcript_samples
from lib.hook_patterns import validate_deep_hooks_content
from lib.paths import DATA_DIR, PATTERN_DIR


def count_transcripts(creator: str) -> int:
    d = DATA_DIR / creator
    if not d.exists():
        return 0
    n = 0
    for video_dir in d.iterdir():
        if not video_dir.is_dir() or video_dir.name.startswith("_"):
            continue
        t = video_dir / "transcript.txt"
        if t.exists() and len(t.read_text(encoding="utf-8", errors="ignore").strip()) >= 50:
            n += 1
    return n


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate deep_hooks.md quality")
    parser.add_argument("creator", help="Creator folder name")
    args = parser.parse_args()

    hook_file = PATTERN_DIR / args.creator / "deep_hooks.md"
    if not hook_file.exists():
        print(f"❌ Missing {hook_file}")
        sys.exit(1)

    content = hook_file.read_text(encoding="utf-8")
    expected = count_transcripts(args.creator)
    video_ids = [
        p.name
        for p in (DATA_DIR / args.creator).iterdir()
        if p.is_dir() and (p / "transcript.txt").exists()
    ] if (DATA_DIR / args.creator).exists() else []

    v = validate_deep_hooks_content(content, expected, video_ids)
    print(f"Transcripts on disk: {expected}")
    print(f"Entries in deep_hooks: {v.entries_found} ({v.entries_complete} complete)")
    if v.missing_videos:
        print(f"Missing video IDs (sample): {v.missing_videos[:10]}")
    for e in v.errors:
        print(f"  ❌ {e}")
    if v.incomplete_entries:
        for x in v.incomplete_entries[:10]:
            print(f"  ⚠️  {x}")

    if v.passed:
        print("✅ Hook library PASSED")
        sys.exit(0)
    print("❌ Hook library NEEDS re-run: python3 deep_hook_learn.py", args.creator)
    sys.exit(1)


if __name__ == "__main__":
    main()
