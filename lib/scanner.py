"""
scanner.py — List Short video IDs and track ingestion state.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import yt_dlp

from lib.ingest_config import IngestConfig
from lib.writer import get_ingestion_summary

RETRYABLE_STATUSES = {"NO_TRANSCRIPT", "RATE_LIMITED", "ERROR", "UNKNOWN", ""}


def scan_channel(creator: dict) -> list[dict]:
    ydl_opts = {"quiet": True, "extract_flat": True, "ignoreerrors": True}
    cfg = IngestConfig.from_env()
    path = cfg.cookies_path()
    if path:
        ydl_opts["cookiefile"] = str(path)
    elif cfg.cookies_from_browser:
        ydl_opts["cookiesfrombrowser"] = (cfg.cookies_from_browser,)
    if cfg.proxy:
        ydl_opts["proxy"] = cfg.proxy

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(creator["url"], download=False)

    videos = []
    for e in info.get("entries") or []:
        if e and e.get("id"):
            videos.append(
                {
                    "id": e["id"],
                    "title": e.get("title", "Unknown"),
                    "url": f"https://www.youtube.com/watch?v={e['id']}",
                }
            )
    return videos


def _read_video_status(creator_dir: str, video_id: str) -> tuple[str, bool]:
    """Return (transcript_status, has_good_txt)."""
    vdir = os.path.join(creator_dir, video_id)
    meta_path = os.path.join(vdir, "metadata.json")
    txt_path = os.path.join(vdir, "transcript.txt")
    has_txt = False
    if os.path.isfile(txt_path):
        try:
            has_txt = len(open(txt_path, encoding="utf-8").read().strip()) > 80
        except OSError:
            has_txt = False

    if not os.path.isfile(meta_path):
        return "", has_txt

    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        status = (meta.get("transcript_status") or "").upper()
        if status == "OK" and has_txt:
            return "OK", True
        return status or "UNKNOWN", has_txt
    except (json.JSONDecodeError, OSError):
        return "UNKNOWN", has_txt


def get_completed_video_ids(data_dir: str, creator_name: str) -> set[str]:
    """Videos with OK transcript on disk."""
    creator_dir = os.path.join(data_dir, creator_name)
    if not os.path.isdir(creator_dir):
        return set()
    done = set()
    for entry in os.scandir(creator_dir):
        if not entry.is_dir() or entry.name.startswith("_"):
            continue
        status, has_txt = _read_video_status(creator_dir, entry.name)
        if status == "OK" and has_txt:
            done.add(entry.name)
    return done


def get_retryable_video_ids(data_dir: str, creator_name: str) -> set[str]:
    """Videos that failed or were rate-limited — safe to re-fetch."""
    creator_dir = os.path.join(data_dir, creator_name)
    if not os.path.isdir(creator_dir):
        return set()
    retry = set()
    for entry in os.scandir(creator_dir):
        if not entry.is_dir() or entry.name.startswith("_"):
            continue
        status, has_txt = _read_video_status(creator_dir, entry.name)
        if status == "OK" and has_txt:
            continue
        if status in RETRYABLE_STATUSES or not has_txt:
            retry.add(entry.name)
    return retry


def get_existing_video_ids(data_dir: str, creator_name: str) -> set[str]:
    """Legacy: all folders with metadata.json (used only with --force off old behavior)."""
    return get_completed_video_ids(data_dir, creator_name)


def filter_new_videos(videos: list[dict], completed_ids: set[str]) -> list[dict]:
    return [v for v in videos if v["id"] not in completed_ids]


def filter_retry_videos(videos: list[dict], retry_ids: set[str]) -> list[dict]:
    return [v for v in videos if v["id"] in retry_ids]


def update_channel_meta(data_dir: str, creator: dict, videos: list[dict]):
    creator_name = creator["name"]
    creator_dir = os.path.join(data_dir, creator_name)
    os.makedirs(creator_dir, exist_ok=True)

    stats = get_ingestion_summary(data_dir, creator_name)
    if "rate_limited" not in stats:
        stats["rate_limited"] = _count_status(data_dir, creator_name, "RATE_LIMITED")

    registry = []
    for v in videos:
        v_id = v["id"]
        status, _ = _read_video_status(creator_dir, v_id)
        registry.append(
            {
                "video_id": v_id,
                "title": v.get("title", "Unknown"),
                "status": status.lower() if status else "pending",
            }
        )

    completed = get_completed_video_ids(data_dir, creator_name)
    meta = {
        "name": creator_name,
        "url": creator["url"],
        "languages": creator["languages"],
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_discovered": len(videos),
        "ingestion_stats": stats,
        "completed_with_transcript": len(completed),
        "completion_percentage": (
            f"{len(completed) / len(videos) * 100:.1f}%" if videos else "0%"
        ),
        "videos": registry,
    }

    with open(os.path.join(creator_dir, "_channel_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


def _count_status(data_dir: str, creator_name: str, status_want: str) -> int:
    n = 0
    creator_dir = os.path.join(data_dir, creator_name)
    if not os.path.isdir(creator_dir):
        return 0
    for entry in os.scandir(creator_dir):
        if entry.is_dir() and not entry.name.startswith("_"):
            st, has_txt = _read_video_status(creator_dir, entry.name)
            if st == status_want:
                n += 1
    return n
