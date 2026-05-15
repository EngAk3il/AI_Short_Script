"""Load Netscape cookies.txt into a requests session (for transcript API)."""
from __future__ import annotations

import http.cookiejar
from pathlib import Path

import requests


def load_session_with_cookies(cookies_path: Path | str) -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        }
    )
    jar = http.cookiejar.MozillaCookieJar(str(cookies_path))
    jar.load(ignore_discard=True, ignore_expires=True)
    session.cookies = jar  # type: ignore[assignment]
    return session
