#!/usr/bin/env python3
"""
prepare.py — Package creator patterns + mission brief for Antigravity/Cursor.

Python does NOT write the script. The agent does live research + intelligent writing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.agent_brief import write_agent_package
from lib.generation_context import load_generation_context, require_hook_library


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare agent intelligence brief (no static script generation)"
    )
    parser.add_argument("--topic", "-t", required=True)
    parser.add_argument("--creator", "-c", required=True)
    parser.add_argument("--topics", help="Batch JSON: [{creator, topic}, ...]")
    args = parser.parse_args()

    if args.topics:
        with open(args.topics, encoding="utf-8") as f:
            items = json.load(f)
        if not isinstance(items, list):
            items = items.get("topics", [])
        for item in items:
            _prepare(item["creator"], item["topic"])
        return

    _prepare(args.creator, args.topic)


def _prepare(creator: str, topic: str) -> None:
    print(f"📦 Preparing agent brief: {creator} / {topic}")
    ctx = load_generation_context(creator, topic)
    try:
        require_hook_library(ctx)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)

    paths = write_agent_package(ctx)
    print(f"\n✅ Agent package ready:")
    print(f"   1. READ FIRST → {paths['brief']}")
    print(f"   2. Context     → {paths['bundle']}")
    print(f"   3. WRITE HERE  → {paths['script']}")
    print(f"\n🧠 Tell Antigravity:")
    print(f'   "Follow {paths["brief"].name} — research the topic live, then write the full script to {paths["script"].name}"')


if __name__ == "__main__":
    main()
