"""Shared ingest configuration (cookies, proxy, delays)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class IngestConfig:
    cookies_file: str | None = None
    cookies_from_browser: str | None = None  # e.g. chrome, firefox, safari
    proxy: str | None = None
    delay_between_videos: float = 8.0
    delay_jitter: float = 4.0
    delay_between_creators: float = 20.0
    pause_every_n: int = 15
    pause_seconds: float = 120.0
    max_retries: int = 4
    retry_base_seconds: float = 30.0
    stop_after_consecutive_blocks: int = 5

    @classmethod
    def from_env(cls) -> "IngestConfig":
        return cls(
            cookies_file=os.environ.get("YT_COOKIES_FILE"),
            cookies_from_browser=os.environ.get("YT_COOKIES_BROWSER"),
            proxy=os.environ.get("YT_PROXY"),
            delay_between_videos=float(os.environ.get("YT_DELAY", "8")),
            pause_every_n=int(os.environ.get("YT_PAUSE_EVERY", "15")),
            pause_seconds=float(os.environ.get("YT_PAUSE_SECONDS", "120")),
        )

    @classmethod
    def marathon(cls) -> "IngestConfig":
        c = cls.from_env()
        c.delay_between_videos = 25.0
        c.delay_jitter = 10.0
        c.delay_between_creators = 45.0
        c.pause_every_n = 8
        c.pause_seconds = 180.0
        return c

    def cookies_path(self) -> Path | None:
        if self.cookies_file and Path(self.cookies_file).is_file():
            return Path(self.cookies_file)
        default = Path(__file__).resolve().parent.parent / "cookies.txt"
        if default.is_file():
            return default
        return None
