#!/usr/bin/env python3
"""Show transcript ingestion progress and what to retry."""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingest import CREATORS_FILE, DATA_DIR, STRATEGY_DATA_DIR, get_data_dir, load_creators
from lib.scanner import get_completed_video_ids, get_retryable_video_ids, scan_channel
from lib.writer import get_ingestion_summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--creator", help="One creator only")
    parser.add_argument("--export-retry-urls", action="store_true", help="Print watch URLs to retry")
    args = parser.parse_args()

    creators = load_creators(CREATORS_FILE)
    if args.creator:
        creators = [c for c in creators if c["name"] == args.creator]

    for c in creators:
        if not c.get("active", True):
            continue
        name = c["name"]
        data_dir = get_data_dir(c)
        summary = get_ingestion_summary(data_dir, name)
        done = get_completed_video_ids(data_dir, name)
        retry = get_retryable_video_ids(data_dir, name)

        try:
            discovered = len(scan_channel(c))
        except Exception:
            discovered = "?"

        print(f"\n{'='*50}")
        print(f"  {name}")
        print(f"  Discovered: {discovered} | OK transcripts: {len(done)}")
        print(f"  Retryable: {len(retry)} | rate_limited: {summary.get('rate_limited', 0)}")
        print(f"  no_transcript: {summary['no_transcript']} | no_speech: {summary['no_speech']}")

        if args.export_retry_urls and retry:
            print("\n  Retry URLs:")
            for vid in sorted(retry)[:30]:
                print(f"    https://www.youtube.com/watch?v={vid}")
            if len(retry) > 30:
                print(f"    ... +{len(retry) - 30} more")

        if retry:
            print(f"\n  → python3 ingest.py -c {name} --retry-failed --cookies cookies.txt --delay 15")


if __name__ == "__main__":
    main()
