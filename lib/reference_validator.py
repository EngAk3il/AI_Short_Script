"""Validate reference URLs in generated scripts."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

import requests

# Bare-domain or homepage-only URLs are not acceptable per SCRIPT_RULES.md
HOMEPAGE_ONLY = re.compile(
    r"^https?://(?:www\.)?[\w.-]+\.(?:com|in|org|net|co\.in)/?$",
    re.I,
)

URL_IN_MARKDOWN = re.compile(r"https?://[^\s\)|\]>\"']+")
REF_TABLE_ROW = re.compile(
    r"^\|\s*\d+\s*\|[^|]+\|[^|]+\|\s*(https?://[^\s|]+)\s*\|",
    re.M,
)

USER_AGENT = (
    "Mozilla/5.0 (compatible; AIShortScript/1.0; +https://github.com/local)"
)


@dataclass
class UrlCheck:
    url: str
    ok: bool
    reason: str = ""


@dataclass
class ReferenceValidation:
    passed: bool
    url_checks: list[UrlCheck] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = []
        for c in self.url_checks:
            mark = "OK" if c.ok else "FAIL"
            lines.append(f"  [{mark}] {c.url[:80]}... — {c.reason}" if len(c.url) > 80 else f"  [{mark}] {c.url} — {c.reason}")
        lines.extend(f"  ERROR: {e}" for e in self.errors)
        lines.extend(f"  WARN: {w}" for w in self.warnings)
        return "\n".join(lines)


def _path_depth(url: str) -> int:
    parsed = urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]
    return len(parts)


def check_url(url: str, timeout: int = 12) -> UrlCheck:
    url = url.rstrip(".,;)")
    if not url.startswith(("http://", "https://")):
        return UrlCheck(url, False, "Not an http(s) URL")

    if HOMEPAGE_ONLY.match(url):
        return UrlCheck(url, False, "Homepage only — need full article path")

    if _path_depth(url) < 1:
        return UrlCheck(url, False, "URL path too shallow — need specific article")

    try:
        resp = requests.head(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
        if resp.status_code == 405:
            resp = requests.get(
                url,
                timeout=timeout,
                allow_redirects=True,
                headers={"User-Agent": USER_AGENT},
                stream=True,
            )
        if resp.status_code >= 400:
            return UrlCheck(url, False, f"HTTP {resp.status_code}")
        final = resp.url
        if _path_depth(final) < 1:
            return UrlCheck(url, False, "Redirects to homepage")
        return UrlCheck(url, True, f"HTTP {resp.status_code}")
    except requests.RequestException as exc:
        return UrlCheck(url, False, str(exc)[:120])


def extract_reference_urls(markdown: str) -> list[str]:
    """Prefer URLs from the references table; fall back to all markdown links in that section."""
    urls: list[str] = []
    if "References" in markdown or "📚" in markdown:
        section = markdown
        for marker in ("### 📚", "## 📚", "### References", "## References"):
            idx = markdown.find(marker)
            if idx != -1:
                section = markdown[idx:]
                break
        for m in REF_TABLE_ROW.finditer(section):
            urls.append(m.group(1).strip())
    if not urls:
        for m in URL_IN_MARKDOWN.finditer(markdown):
            u = m.group(0).rstrip(".,;)")
            if "youtube.com" not in u and "youtu.be" not in u:
                urls.append(u)
    # dedupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def validate_references(markdown: str, min_refs: int = 2) -> ReferenceValidation:
    result = ReferenceValidation(passed=True)

    if "References" not in markdown and "📚" not in markdown:
        result.passed = False
        result.errors.append("Missing 📚 References & Sources section")
        return result

    urls = extract_reference_urls(markdown)
    if len(urls) < min_refs:
        result.passed = False
        result.errors.append(
            f"Need at least {min_refs} reference URLs in table; found {len(urls)}"
        )

    for url in urls:
        check = check_url(url)
        result.url_checks.append(check)
        if not check.ok:
            result.passed = False
            result.errors.append(f"Invalid reference: {url} — {check.reason}")

    if "[URL VERIFICATION NEEDED]" in markdown or "[UNVERIFIED" in markdown:
        result.warnings.append("Script contains unverified placeholders")

    return result
