#!/usr/bin/env python3
"""Show deep_hooks.md coverage vs transcripts on disk."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.deep_hooks_builder import load_transcripts, parse_covered_video_ids
from lib.hook_patterns import validate_deep_hooks_content
from lib.paths import PATTERN_DIR


def main() -> None:
    creators = sys.argv[1:] if len(sys.argv) > 1 else sorted(
        d.name for d in PATTERN_DIR.iterdir() if d.is_dir()
    )
    print(f"{'Creator':<22} {'Transcripts':>11} {'In deep_hooks':>13} {'Coverage':>9}")
    print("-" * 60)
    for c in creators:
        txs = load_transcripts(c)
        hf = PATTERN_DIR / c / "deep_hooks.md"
        if not txs:
            continue
        if not hf.exists():
            print(f"{c:<22} {len(txs):>11} {'0':>13} {'0%':>9}")
            continue
        content = hf.read_text(encoding="utf-8")
        covered = parse_covered_video_ids(content)
        matched = sum(1 for t in txs if t.video_id in covered)
        pct = matched / len(txs) * 100 if txs else 0
        flag = "✅" if pct >= 95 else "⚠️ " if pct >= 50 else "❌"
        print(f"{flag} {c:<20} {len(txs):>11} {matched:>13} {pct:>8.0f}%")
        if pct < 95:
            missing = [t.video_id for t in txs if t.video_id not in covered]
            print(f"     → python3 deep_hook_learn.py {c}")


if __name__ == "__main__":
    main()
