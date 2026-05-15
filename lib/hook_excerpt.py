"""Extract topic-relevant lines from deep_hooks.md for context bundles."""

from __future__ import annotations

import re


def excerpt_deep_hooks(deep_hooks: str, topic: str, max_chars: int = 4500) -> str:
    if not deep_hooks.strip():
        return "(no deep_hooks.md — use hook cheatsheet only)"

    words = [w.lower() for w in re.findall(r"[a-zA-Z\u0900-\u097F]{3,}", topic)]
    if not words:
        return deep_hooks[-max_chars:]

    blocks = re.split(r"\n(?=#{1,3}\s|\*\*Video:|\[Video:)", deep_hooks)
    scored: list[tuple[int, str]] = []
    for block in blocks:
        if len(block.strip()) < 80:
            continue
        bl = block.lower()
        score = sum(3 for w in words if w in bl)
        if score > 0:
            scored.append((score, block.strip()))

    scored.sort(key=lambda x: -x[0])
    chosen = scored[:4]
    if not chosen:
        return deep_hooks[-max_chars:]

    out = ["## Topic-matched hooks (mirror rhythm — do not copy facts)\n"]
    total = 0
    for score, block in chosen:
        chunk = f"### Match score {score}\n{block[:1200]}\n"
        if total + len(chunk) > max_chars:
            break
        out.append(chunk)
        total += len(chunk)
    return "\n".join(out)
