"""
transcript.py — Fetch timed transcripts with retries, cookies, and proxy support.

Level 1: youtube-transcript-api (with optional cookies session + proxy)
Level 2: yt-dlp subtitles (json3 / vtt) — works well with cookies.txt
Level 3: metadata-only → NO_TRANSCRIPT or RATE_LIMITED (retry later)
"""

from __future__ import annotations

import json
import logging
import re
import tempfile
from pathlib import Path

import requests
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled

from lib.ingest_config import IngestConfig
from lib.rate_limit import is_rate_limit_error, retry_with_backoff

logger = logging.getLogger(__name__)

# Module-level config set by ingest.py before fetching
_active_config: IngestConfig | None = None
_last_block: bool = False


def configure_ingest(config: IngestConfig | None) -> None:
    global _active_config
    _active_config = config


def was_last_fetch_blocked() -> bool:
    return _last_block


class TranscriptResult:
    def __init__(self, video_id: str):
        self.video_id = video_id
        self.segments: list[dict] = []
        self.language: str | None = None
        self.source: str | None = None
        self.status: str | None = None  # OK, NO_TRANSCRIPT, NO_SPEECH, RATE_LIMITED
        self.title: str | None = None
        self.description: str | None = None
        self.duration_seconds: int | None = None
        self.publish_date: str | None = None
        self.error: str | None = None


def _config() -> IngestConfig:
    return _active_config or IngestConfig.from_env()


def _build_ydl_opts(extra: dict | None = None) -> dict:
    cfg = _config()
    opts: dict = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "socket_timeout": 30,
        "retries": 3,
        "fragment_retries": 3,
        "sleep_interval_requests": 1.5,
        "sleep_interval": 2,
    }
    if cfg.proxy:
        opts["proxy"] = cfg.proxy
    path = cfg.cookies_path()
    if path:
        opts["cookiefile"] = str(path)
    elif cfg.cookies_from_browser:
        opts["cookiesfrombrowser"] = (cfg.cookies_from_browser,)
    if extra:
        opts.update(extra)
    return opts


def _build_transcript_api() -> YouTubeTranscriptApi:
    cfg = _config()
    session: requests.Session | None = None
    path = cfg.cookies_path()
    if path:
        from lib.cookies_loader import load_session_with_cookies

        session = load_session_with_cookies(path)
    if cfg.proxy and session:
        session.proxies = {"http": cfg.proxy, "https": cfg.proxy}
    elif cfg.proxy:
        session = requests.Session()
        session.proxies = {"http": cfg.proxy, "https": cfg.proxy}

    if session:
        return YouTubeTranscriptApi(http_client=session)
    return YouTubeTranscriptApi()


def fetch_transcript(video_id: str, languages: list[str] | None = None) -> TranscriptResult:
    global _last_block
    _last_block = False

    if languages is None:
        languages = ["hi", "en", "en-IN", "hi-IN"]

    result = TranscriptResult(video_id)
    cfg = _config()
    blocked = False

    try:
        retry_with_backoff(
            lambda: _fetch_metadata(result),
            max_retries=cfg.max_retries,
            base_seconds=cfg.retry_base_seconds,
            label=f"metadata:{video_id}",
        )
    except Exception as e:
        if is_rate_limit_error(e):
            blocked = True
            result.error = str(e)[:200]
        else:
            logger.warning("[%s] Metadata fetch failed: %s", video_id, e)

    if result.status != "NO_SPEECH":
        try:
            if _try_level1(result, languages):
                return result
        except Exception as e:
            if is_rate_limit_error(e):
                blocked = True
                result.error = str(e)[:200]

        try:
            if _try_level2(result, languages):
                return result
        except Exception as e:
            if is_rate_limit_error(e):
                blocked = True
                result.error = str(e)[:200]

    _finalize(result, blocked=blocked)
    _last_block = blocked
    return result


def _fetch_metadata(result: TranscriptResult) -> None:
    with yt_dlp.YoutubeDL(_build_ydl_opts()) as ydl:
        info = ydl.extract_info(
            f"https://www.youtube.com/watch?v={result.video_id}",
            download=False,
        )
    result.title = info.get("title", "Unknown")
    result.description = info.get("description", "")
    result.duration_seconds = info.get("duration")
    result.publish_date = info.get("upload_date")
    auto_caps = info.get("automatic_captions") or {}
    manual_subs = info.get("subtitles") or {}
    if not auto_caps and not manual_subs:
        result.status = "NO_SPEECH"
        result.error = "No captions available on YouTube"


def _try_level1(result: TranscriptResult, languages: list[str]) -> bool:
    if result.status == "NO_SPEECH":
        return False

    cfg = _config()

    def _fetch():
        api = _build_transcript_api()
        transcript = api.fetch(result.video_id, languages=languages)
        segments = [
            {"start": s.start, "duration": s.duration, "text": s.text}
            for s in transcript.snippets
        ]
        if not segments:
            return None
        result.segments = segments
        result.language = transcript.language
        result.source = "youtube-transcript-api"
        result.status = "OK"
        return True

    try:
        out = retry_with_backoff(
            _fetch,
            max_retries=cfg.max_retries,
            base_seconds=cfg.retry_base_seconds,
            label=f"L1:{result.video_id}",
        )
        if out:
            logger.info(
                "[%s] L1 OK: %d segments lang=%s",
                result.video_id,
                len(result.segments),
                result.language,
            )
        return bool(out)
    except NoTranscriptFound:
        logger.info("[%s] L1: no transcript for %s", result.video_id, languages)
    except TranscriptsDisabled:
        logger.info("[%s] L1: transcripts disabled", result.video_id)
    except Exception as e:
        if is_rate_limit_error(e):
            raise
        logger.info("[%s] L1 failed: %s", result.video_id, str(e)[:100])
    return False


def _try_level2(result: TranscriptResult, languages: list[str]) -> bool:
    if result.status == "NO_SPEECH":
        return False

    cfg = _config()
    langs_try = list(dict.fromkeys(languages + ["en", "hi"]))

    def _run():
        with tempfile.TemporaryDirectory() as tmp:
            outtmpl = str(Path(tmp) / "%(id)s")
            opts = _build_ydl_opts(
                {
                    "writeautomaticsub": True,
                    "writesubtitles": True,
                    "subtitleslangs": langs_try,
                    "subtitlesformat": "json3/vtt/best",
                    "skip_download": True,
                    "outtmpl": outtmpl,
                }
            )
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(
                    f"https://www.youtube.com/watch?v={result.video_id}",
                    download=True,
                )
                if not result.title:
                    result.title = info.get("title", "Unknown")

            # Find downloaded sub files
            for lang in langs_try:
                for pattern in (f"{result.video_id}.{lang}.json3", f"{result.video_id}.{lang}.vtt"):
                    fpath = Path(tmp) / pattern
                    if not fpath.exists():
                        continue
                    segments = (
                        _parse_json3_file(fpath)
                        if fpath.suffix == ".json3"
                        else _parse_vtt_file(fpath)
                    )
                    if segments:
                        result.segments = segments
                        result.language = lang
                        result.source = "yt-dlp-sub"
                        result.status = "OK"
                        return True

            # Fallback: requested_subtitles URL
            with yt_dlp.YoutubeDL(_build_ydl_opts()) as ydl:
                info = ydl.extract_info(
                    f"https://www.youtube.com/watch?v={result.video_id}",
                    download=False,
                )
            req_subs = info.get("requested_subtitles") or {}
            for lang in langs_try:
                if lang not in req_subs:
                    continue
                sub_url = req_subs[lang].get("url")
                if not sub_url:
                    continue
                segments = _download_sub_url(sub_url)
                if segments:
                    result.segments = segments
                    result.language = lang
                    result.source = "yt-dlp-auto-sub"
                    result.status = "OK"
                    return True
        return False

    try:
        ok = retry_with_backoff(
            _run,
            max_retries=cfg.max_retries,
            base_seconds=cfg.retry_base_seconds,
            label=f"L2:{result.video_id}",
        )
        if ok:
            logger.info(
                "[%s] L2 OK: %d segments lang=%s",
                result.video_id,
                len(result.segments),
                result.language,
            )
        return ok
    except Exception as e:
        if is_rate_limit_error(e):
            raise
        logger.info("[%s] L2 failed: %s", result.video_id, str(e)[:100])
    return False


def _download_sub_url(url: str) -> list[dict]:
    cfg = _config()
    session = requests.Session()
    path = cfg.cookies_path()
    if path:
        from lib.cookies_loader import load_session_with_cookies

        session = load_session_with_cookies(path)
    if cfg.proxy:
        session.proxies = {"http": cfg.proxy, "https": cfg.proxy}
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    if "json" in url or resp.text.strip().startswith("{"):
        return _parse_json3_bytes(resp.content)
    return _parse_vtt_text(resp.text)


def _parse_json3_file(path: Path) -> list[dict]:
    return _parse_json3_bytes(path.read_bytes())


def _parse_json3_bytes(data: bytes) -> list[dict]:
    try:
        obj = json.loads(data)
    except json.JSONDecodeError:
        return []
    segments = []
    for ev in obj.get("events", []):
        segs = ev.get("segs", [])
        if not segs:
            continue
        text = "".join(s.get("utf8", "") for s in segs).strip()
        if text and text != "\n":
            t_ms = ev.get("tStartMs", 0)
            d_ms = ev.get("dDurationMs", 0)
            segments.append(
                {"start": t_ms / 1000.0, "duration": d_ms / 1000.0, "text": text}
            )
    return segments


def _parse_vtt_file(path: Path) -> list[dict]:
    return _parse_vtt_text(path.read_text(encoding="utf-8", errors="ignore"))


def _parse_vtt_text(text: str) -> list[dict]:
    segments = []
    lines = text.splitlines()
    i = 0
    timestamp_re = re.compile(
        r"(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})\.(\d{3})"
    )

    def _to_sec(h, m, s, ms) -> float:
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

    while i < len(lines):
        m = timestamp_re.match(lines[i].strip())
        if m:
            start = _to_sec(*m.groups()[:4])
            end = _to_sec(*m.groups()[4:])
            i += 1
            text_lines = []
            while i < len(lines) and lines[i].strip() and "-->" not in lines[i]:
                line = re.sub("<[^>]+>", "", lines[i]).strip()
                if line:
                    text_lines.append(line)
                i += 1
            if text_lines:
                segments.append(
                    {
                        "start": start,
                        "duration": max(0.1, end - start),
                        "text": " ".join(text_lines),
                    }
                )
            continue
        i += 1
    return segments


def _finalize(result: TranscriptResult, blocked: bool = False) -> None:
    if result.status == "OK":
        return
    if result.status == "NO_SPEECH":
        logger.info("[%s] Final: NO_SPEECH", result.video_id)
        return
    if blocked:
        result.status = "RATE_LIMITED"
        result.error = result.error or "YouTube rate limit / IP block — retry later with cookies"
        logger.warning("[%s] Final: RATE_LIMITED", result.video_id)
        return
    result.status = "NO_TRANSCRIPT"
    result.error = result.error or "All extraction methods failed"
    logger.info("[%s] Final: NO_TRANSCRIPT", result.video_id)
