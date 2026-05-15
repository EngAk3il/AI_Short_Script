#!/usr/bin/env python3
"""Validate a generated script: structure, retention, reference URLs."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.reference_validator import validate_references
from lib.script_validator import validate_script


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate script markdown")
    parser.add_argument("script", help="Path to .md script")
    parser.add_argument("--creator", "-c", default="", help="Creator name for context")
    parser.add_argument("--min-refs", type=int, default=2)
    args = parser.parse_args()

    path = Path(args.script)
    if not path.exists():
        print(f"❌ Not found: {path}")
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    sv = validate_script(text, args.creator)
    rv = validate_references(text, min_refs=args.min_refs)

    print("=== Script structure ===")
    print(f"Passed: {sv.passed}  Score: {sv.score}/{sv.max_score}")
    for e in sv.errors:
        print(f"  ❌ {e}")
    for w in sv.warnings:
        print(f"  ⚠️  {w}")

    print("\n=== Reference URLs ===")
    print(f"Passed: {rv.passed}")
    print(rv.summary())

    if sv.passed and rv.passed:
        print("\n✅ Overall: PASSED")
        sys.exit(0)
    print("\n❌ Overall: FAILED")
    sys.exit(1)


if __name__ == "__main__":
    main()
