#!/usr/bin/env python3
"""
ingest.py — Fetch YouTube Shorts transcripts reliably (cookies + retry + resume).

Usage:
    python3 ingest.py -c Shivanshu.Agrawal
    python3 ingest.py -c GenZway --retry-failed
    python3 ingest.py -c GenZway --cookies cookies.txt --delay 15
    python3 ingest.py -c GenZway --cookies-from-browser chrome
    python3 ingest_status.py -c GenZway
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.ingest_config import IngestConfig
from lib.rate_limit import sleep_with_jitter
from lib.scanner import (
    filter_new_videos,
    filter_retry_videos,
    get_completed_video_ids,
    get_retryable_video_ids,
    scan_channel,
    update_channel_meta,
)
from lib.transcript import configure_ingest, fetch_transcript, was_last_fetch_blocked
from lib.writer import get_ingestion_summary, write_video_data

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
STRATEGY_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "strategy_data")
CREATORS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "creators.json")
STATE_FILE = "_ingest_state.json"


def get_data_dir(creator: dict) -> str:
    if creator.get("type") == "strategy":
        return STRATEGY_DATA_DIR
    return DATA_DIR


def load_creators(filepath: str) -> list[dict]:
    with open(filepath, encoding="utf-8") as f:
        return json.load(f).get("creators", [])


def ingest_single_video(creator: dict, video: dict, all_videos: list[dict]) -> str:
    name = creator["name"]
    languages = creator.get("languages", ["hi", "en"])
    v_id = video["id"]
    v_title = video.get("title", "Unknown")
    current_data_dir = get_data_dir(creator)

    print(f"\n   -> {v_id} — {v_title[:50]}")

    try:
        result = fetch_transcript(v_id, languages=languages)
        write_video_data(current_data_dir, name, result)
        status = (result.status or "error").lower()

        icons = {
            "ok": "✅",
            "rate_limited": "🚫",
            "no_transcript": "❌",
            "no_speech": "🔇",
        }
        icon = icons.get(status, "❓")
        seg_count = len(result.segments) if result.segments else 0
        print(
            f"       {icon} {status} | {seg_count} segments | "
            f"lang={result.language} | via={result.source}"
        )
        if result.error and status != "ok":
            print(f"       ↳ {result.error[:100]}")

        update_channel_meta(current_data_dir, creator, all_videos)
        return status

    except Exception as e:
        print(f"       💥 Error: {e}")
        return "error"


def save_state(data_dir: str, creator: str, queue: list[dict]) -> None:
    path = os.path.join(data_dir, creator, STATE_FILE)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"remaining": [v["id"] for v in queue]}, f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest YouTube Shorts transcripts")
    parser.add_argument("--creator", "-c", help="Creator name from creators.json")
    parser.add_argument("--limit", "-l", type=int, default=0, help="Max videos per creator")
    parser.add_argument("--force", "-f", action="store_true", help="Re-fetch all videos")
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Only retry NO_TRANSCRIPT / RATE_LIMITED / missing transcript.txt",
    )
    parser.add_argument("--marathon", "-m", action="store_true", help="Slower delays + longer pauses")
    parser.add_argument("--delay", type=float, default=0, help="Seconds between videos (default 8)")
    parser.add_argument("--cookies", help="Path to cookies.txt (Netscape format)")
    parser.add_argument(
        "--cookies-from-browser",
        help="Load cookies from browser: chrome, firefox, safari, edge",
    )
    parser.add_argument("--proxy", help="HTTP/S proxy URL")
    parser.add_argument("--pause-every", type=int, default=0, help="Long pause every N videos")
    parser.add_argument("--pause-seconds", type=float, default=120, help="Long pause duration")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    cfg = IngestConfig.marathon() if args.marathon else IngestConfig.from_env()
    if args.delay > 0:
        cfg.delay_between_videos = args.delay
    if args.cookies:
        cfg.cookies_file = args.cookies
    if args.cookies_from_browser:
        cfg.cookies_from_browser = args.cookies_from_browser
    if args.proxy:
        cfg.proxy = args.proxy
    if args.pause_every > 0:
        cfg.pause_every_n = args.pause_every
        cfg.pause_seconds = args.pause_seconds

    configure_ingest(cfg)

    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    creators = load_creators(CREATORS_FILE)
    if args.creator:
        creators = [c for c in creators if c["name"] == args.creator]
        if not creators:
            print(f"❌ Creator '{args.creator}' not found")
            sys.exit(1)

    active = [c for c in creators if c.get("active", True)]
    if not active:
        print("❌ No active creators")
        sys.exit(1)

    has_cookies = bool(cfg.cookies_path() or cfg.cookies_from_browser)
    print("🚀 Transcript ingest (resilient mode)")
    print(f"   Creators: {len(active)}")
    print(f"   Delay: {cfg.delay_between_videos}s (+{cfg.delay_jitter}s jitter)")
    print(f"   Pause: every {cfg.pause_every_n} videos → {cfg.pause_seconds}s")
    print(f"   Cookies: {'✅ yes' if has_cookies else '⚠️  none — export cookies.txt (see INGEST.md)'}")
    if cfg.proxy:
        print(f"   Proxy: {cfg.proxy}")

    creator_queues = []
    total = 0

    for creator in active:
        name = creator["name"]
        data_dir = get_data_dir(creator)
        print(f"\n📡 {name}...", end="", flush=True)
        videos = scan_channel(creator)

        if args.force:
            todo = videos
        elif args.retry_failed:
            retry_ids = get_retryable_video_ids(data_dir, name)
            todo = filter_retry_videos(videos, retry_ids)
        else:
            done = get_completed_video_ids(data_dir, name)
            todo = filter_new_videos(videos, done)

        if args.limit > 0:
            todo = todo[: args.limit]

        update_channel_meta(data_dir, creator, videos)
        print(f" {len(todo)} to process / {len(videos)} total")
        if todo:
            creator_queues.append({"creator": creator, "all_videos": videos, "queue": todo})
            total += len(todo)

    if total == 0:
        print("\n✅ Nothing to process. Use --retry-failed for blocked videos.")
        return

    print(f"\n📦 Processing {total} videos...")
    processed = 0
    consecutive_blocks = 0

    while any(q["queue"] for q in creator_queues):
        for q in creator_queues:
            if not q["queue"]:
                continue

            creator = q["creator"]
            data_dir = get_data_dir(creator)
            video = q["queue"].pop(0)
            processed += 1

            print(f"\n[{processed}/{total}] {creator['name']}")
            status = ingest_single_video(creator, video, q["all_videos"])
            save_state(data_dir, creator["name"], q["queue"])

            if status == "rate_limited" or was_last_fetch_blocked():
                consecutive_blocks += 1
            else:
                consecutive_blocks = 0

            if consecutive_blocks >= cfg.stop_after_consecutive_blocks:
                print(
                    f"\n🛑 Stopping: {consecutive_blocks} consecutive blocks. "
                    "Export cookies.txt and run:\n"
                    f"   python3 ingest.py -c {creator['name']} --retry-failed "
                    f"--cookies cookies.txt --delay 20\n"
                    "See INGEST.md"
                )
                sys.exit(2)

            if processed < total:
                if cfg.pause_every_n and processed % cfg.pause_every_n == 0:
                    print(f"\n   ☕ Cooldown {cfg.pause_seconds}s after {processed} videos...")
                    time.sleep(cfg.pause_seconds)
                else:
                    sleep_with_jitter(cfg.delay_between_videos, cfg.delay_jitter)

    print(f"\n{'='*60}\n  🎉 INGESTION COMPLETE\n{'='*60}")
    for creator in active:
        d = get_data_dir(creator)
        s = get_ingestion_summary(d, creator["name"])
        print(
            f"\n  {creator['name']}: total={s['total']} ok={s['ok']} "
            f"blocked={s.get('rate_limited', 0)} no_tx={s['no_transcript']} no_speech={s['no_speech']}"
        )


if __name__ == "__main__":
    main()
