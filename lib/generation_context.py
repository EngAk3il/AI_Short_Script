"""Load all assets needed for script generation."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from lib.creator_profiles import CREATOR_CONTEXT
from lib.voice_purity import sanitize_framework_for_creator, sanitize_voice_text
from lib.paths import (
    DATA_DIR,
    PATTERN_DIR,
    PATTERNS_DIR,
    SCRIPT_RULES,
    SHORTS_FRAMEWORK,
)


@dataclass
class GenerationContext:
    creator: str
    topic: str
    creator_mind: str = ""
    deep_hooks: str = ""
    hook_cheatsheet: str = ""
    dna_md: str = ""
    samples: list[str] = field(default_factory=list)
    facts: dict = field(default_factory=dict)
    script_rules: str = ""
    framework: str = ""
    creator_bio: str = ""

    def cheatsheet_or_hooks_summary(self, max_chars: int = 12000) -> str:
        if self.hook_cheatsheet:
            return self.hook_cheatsheet[:max_chars]
        return self.deep_hooks[:max_chars]

    def hooks_for_prompt(self, max_chars: int = 14000) -> str:
        """Cheatsheet first, then tail of deep hooks for per-video patterns."""
        parts = []
        if self.hook_cheatsheet:
            parts.append("## HOOK CHEATSHEET\n" + self.hook_cheatsheet[:8000])
        if self.deep_hooks:
            remaining = max_chars - sum(len(p) for p in parts)
            if remaining > 2000:
                parts.append(
                    "## DEEP HOOK LIBRARY (per-transcript patterns)\n"
                    + self.deep_hooks[-remaining:]
                )
        return "\n\n".join(parts)[:max_chars]


def _read_optional(path: Path, max_chars: int | None = None) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="ignore")
    if max_chars:
        return text[:max_chars]
    return text


def _video_quality_score(video_dir: Path) -> int:
    score = 0
    meta_path = video_dir / "metadata.json"
    t_path = video_dir / "transcript.txt"
    if not t_path.exists():
        return 0
    text = t_path.read_text(encoding="utf-8", errors="ignore").strip()
    score += min(len(text) // 50, 40)
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if meta.get("transcript_status") == "OK":
                score += 20
            views = meta.get("view_count") or meta.get("views") or 0
            if isinstance(views, int):
                score += min(views // 100_000, 30)
        except json.JSONDecodeError:
            pass
    return score


def load_transcript_samples(creator: str, n: int = 5) -> list[str]:
    creator_dir = DATA_DIR / creator
    if not creator_dir.exists():
        return []

    candidates: list[tuple[int, Path]] = []
    for video_dir in creator_dir.iterdir():
        if not video_dir.is_dir() or video_dir.name.startswith("_"):
            continue
        score = _video_quality_score(video_dir)
        if score > 5:
            candidates.append((score, video_dir))

    candidates.sort(key=lambda x: -x[0])
    samples: list[str] = []
    for _, video_dir in candidates[:n]:
        text = (video_dir / "transcript.txt").read_text(encoding="utf-8", errors="ignore").strip()
        title = video_dir.name
        meta_path = video_dir / "metadata.json"
        if meta_path.exists():
            try:
                title = json.loads(meta_path.read_text()).get("title", title)
            except json.JSONDecodeError:
                pass
        samples.append(f"[Video: {video_dir.name} | {title}]\n{text[:2500]}")
    return samples


def load_generation_context(
    creator: str,
    topic: str,
    facts: dict | None = None,
) -> GenerationContext:
    pattern_dir = PATTERN_DIR / creator
    creator_mind = sanitize_voice_text(
        _read_optional(pattern_dir / "CREATOR_MIND.md"), creator
    )
    hook_cheatsheet = sanitize_voice_text(
        _read_optional(pattern_dir / "hook_cheatsheet.md"), creator
    )
    dna_md = sanitize_voice_text(
        _read_optional(PATTERNS_DIR / creator / "dna.md", max_chars=10000), creator
    )
    ctx = GenerationContext(
        creator=creator,
        topic=topic,
        creator_mind=creator_mind,
        deep_hooks=_read_optional(pattern_dir / "deep_hooks.md"),
        hook_cheatsheet=hook_cheatsheet,
        dna_md=dna_md,
        samples=load_transcript_samples(creator, n=6),
        facts=facts or {},
        script_rules=_read_optional(SCRIPT_RULES, max_chars=5000),
        framework=sanitize_framework_for_creator(
            _read_optional(SHORTS_FRAMEWORK, max_chars=6000), creator
        ),
        creator_bio=CREATOR_CONTEXT.get(creator, ""),
    )
    return ctx


def require_hook_library(ctx: GenerationContext) -> None:
    if not ctx.creator_mind and not ctx.deep_hooks and not ctx.hook_cheatsheet:
        raise FileNotFoundError(
            f"No pattern library for '{ctx.creator}'. "
            f"Run: python3 deep_hook_learn.py {ctx.creator} "
            f"and ensure creator_pattern/{ctx.creator}/CREATOR_MIND.md exists"
        )
