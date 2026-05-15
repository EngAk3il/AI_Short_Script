#!/usr/bin/env python3
"""
daily_script.py — Daily script generation (calls full generate pipeline).
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingest import CREATORS_FILE, load_creators


def get_next_creator(creators: list) -> dict:
    day_of_year = datetime.now().timetuple().tm_yday
    return creators[day_of_year % len(creators)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily automated script generation")
    parser.add_argument("--topic", "-t", help="Topic (required unless --discover)")
    parser.add_argument("--creator", "-c", help="Creator name")
    parser.add_argument("--no-research", action="store_true")
    args = parser.parse_args()

    creators = [c for c in load_creators(CREATORS_FILE) if c.get("active", True)]
    if not creators:
        print("❌ No active creators in creators.json")
        sys.exit(1)

    creator = (
        next((c for c in creators if c["name"] == args.creator), None)
        if args.creator
        else get_next_creator(creators)
    )
    if not creator:
        print(f"❌ Creator '{args.creator}' not found")
        sys.exit(1)

    topic = args.topic
    if not topic:
        print("❌ Provide --topic for daily run (trend discovery is manual via Antigravity)")
        sys.exit(1)

    print(f"📅 Daily — {datetime.now().strftime('%Y-%m-%d')}")
    print(f"👤 {creator['name']} | 💡 {topic}")

    cmd = [
        sys.executable,
        os.path.join(os.path.dirname(__file__), "prepare.py"),
        "--creator",
        creator["name"],
        "--topic",
        topic,
    ]

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
