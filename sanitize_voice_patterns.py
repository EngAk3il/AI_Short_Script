#!/usr/bin/env python3
"""Rewrite CREATOR_MIND / hook_cheatsheet / dna.md — remove other-creator names."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.paths import PATTERN_DIR, PATTERNS_DIR
from lib.voice_purity import sanitize_voice_text


def main() -> None:
    updated = 0
    for mind in sorted(PATTERN_DIR.glob("*/CREATOR_MIND.md")):
        creator = mind.parent.name
        text = mind.read_text(encoding="utf-8")
        clean = sanitize_voice_text(text, creator)
        if clean != text:
            mind.write_text(clean, encoding="utf-8")
            print(f"✓ {mind.relative_to(PATTERN_DIR.parent)}")
            updated += 1

    for cheat in sorted(PATTERN_DIR.glob("*/hook_cheatsheet.md")):
        creator = cheat.parent.name
        text = cheat.read_text(encoding="utf-8")
        clean = sanitize_voice_text(text, creator)
        if clean != text:
            cheat.write_text(clean, encoding="utf-8")
            print(f"✓ {cheat.relative_to(PATTERN_DIR.parent)}")
            updated += 1

    dna_dir = PATTERNS_DIR
    if dna_dir.exists():
        for dna in sorted(dna_dir.glob("*/dna.md")):
            creator = dna.parent.name
            text = dna.read_text(encoding="utf-8")
            clean = sanitize_voice_text(text, creator)
            if clean != text:
                dna.write_text(clean, encoding="utf-8")
                print(f"✓ {dna.relative_to(PATTERNS_DIR.parent)}")
                updated += 1

    print(f"\nDone. {updated} file(s) cleaned.")


if __name__ == "__main__":
    main()
