"""Strip other-creator names from voice docs so agents only see pure channel style."""

from __future__ import annotations

import json
import re
from pathlib import Path

from lib.paths import CREATORS_FILE

# Display names / aliases that appear in legacy pattern files
EXTRA_ALIASES: dict[str, list[str]] = {
    "Shivanshu.Agrawal": ["Shivanshu", "designbyarpit"],
    "PrabhjotSpeaks": ["Prabhjot"],
    "ThinkSchool_Hindi": ["Think School", "ThinkSchool"],
    "hellooipsita": ["Ipsita", "hellooipsita"],
    "GenZway": ["Gen Z way"],
    "NehaGupta": ["Neha Gupta"],
    "KKCreate": ["KK Create"],
    "NiharikaChoudhary": ["Niharika"],
    "TheInformedCitizen": ["Informed Citizen"],
    "Nitishrajputshorts": ["Nitish", "NitishRajput"],
    "Finsaheliofficial": ["Finsaheli"],
    "openletteryt": ["open letter"],
    "UditInsights": ["Udit"],
    "AshutoshPratihastAP": ["Ashutosh"],
    "MangeshShinde": ["Mangesh"],
}

_LEGACY_NAMES = ["designbyarpit", "SciCoLens", "CleoAbram", "FullDisclosure"]


def load_all_creator_tokens() -> list[str]:
    path = CREATORS_FILE
    names: list[str] = []
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        for c in data.get("creators", []):
            if c.get("name"):
                names.append(c["name"])
    names.extend(_LEGACY_NAMES)
    return sorted(set(names), key=len, reverse=True)


def _active_name_variants(active: str) -> set[str]:
    """Names that refer to the assigned creator — must never be stripped."""
    variants = {active.lower()}
    for part in active.replace(".", " ").replace("_", " ").split():
        if len(part) > 2:
            variants.add(part.lower())
    for alias in EXTRA_ALIASES.get(active, []):
        variants.add(alias.lower())
    return variants


def _tokens_for_creator(active: str) -> list[str]:
    active_variants = _active_name_variants(active)
    tokens = load_all_creator_tokens()
    out: list[str] = []
    for t in tokens:
        tl = t.lower()
        if tl in active_variants:
            continue
        if any(v in tl or tl in v for v in active_variants if len(v) > 4):
            continue
        out.append(t)
    for other_name, aliases in EXTRA_ALIASES.items():
        if other_name.lower() == active.lower():
            continue
        out.append(other_name)
        out.extend(aliases)
    return sorted(set(out), key=len, reverse=True)


def _line_mentions_other(line: str, others: list[str], active: str) -> bool:
    low = line.lower()
    active_variants = _active_name_variants(active)
    for o in others:
        ol = o.lower()
        if ol in active_variants:
            continue
        if re.search(r"\b" + re.escape(ol) + r"\b", low):
            return True
    return False


def _extract_trait_parentheticals(
    line: str, others: list[str], active: str
) -> str | None:
    """Pull (no bhai) style hints from NOT lines without other creator names."""
    traits: list[str] = []
    for inner in re.findall(r"\(([^)]*)\)", line):
        if _line_mentions_other(inner, others, active):
            continue
        inner = inner.strip()
        if inner and len(inner) < 120:
            traits.append(inner)
    if traits:
        return "- **Avoid:** " + "; ".join(traits)
    return None


def _clean_comparison_line(line: str, others: list[str]) -> str:
    cleaned = line
    for o in others:
        cleaned = re.sub(
            r",?\s*\(?\s*like\s+" + re.escape(o) + r"[^).]*\)?",
            "",
            cleaned,
            flags=re.I,
        )
        cleaned = re.sub(
            r",?\s*\(?\s*that'?s\s+" + re.escape(o) + r"[^).]*\)?",
            "",
            cleaned,
            flags=re.I,
        )
        cleaned = re.sub(
            r"\b" + re.escape(o) + r"[^,;.]*",
            "",
            cleaned,
            flags=re.I,
        )
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    cleaned = re.sub(r"\(\s*\)", "", cleaned)
    return cleaned


def sanitize_voice_text(text: str, active_creator: str) -> str:
    """
    Remove references to other channels from CREATOR_MIND / dna / cheatsheets.
    Keeps only trait-based rules so agents do not mimic or name other creators.
    """
    if not text.strip():
        return text

    others = _tokens_for_creator(active_creator)
    out: list[str] = []

    for line in text.splitlines():
        raw = line
        if not _line_mentions_other(line, others, active_creator):
            out.append(raw)
            continue

        if line.strip().startswith("# CREATOR MIND:"):
            out.append(line)
            continue

        if re.search(r"cross[- ]contamination", line, re.I):
            out.append(
                "- [ ] **Pure voice only** — hooks, CTAs, and tone match "
                f"`{active_creator}` transcripts only"
            )
            continue

        if re.search(r"\b(NOT|Never|Avoid)\b", line, re.I):
            trait_line = _extract_trait_parentheticals(line, others, active_creator)
            if trait_line:
                out.append(trait_line)
            elif re.search(r"\*\*Avoid:\*\*", line, re.I):
                cleaned = _clean_comparison_line(line, others)
                if cleaned and not _line_mentions_other(cleaned, others, active_creator):
                    out.append(cleaned)
            continue

        if re.search(r"\blike\b", line, re.I) or "entire system" in line.lower():
            cleaned = _clean_comparison_line(line, others)
            if (
                cleaned
                and not _line_mentions_other(cleaned, others, active_creator)
                and len(cleaned) > 20
            ):
                out.append(cleaned)
            continue

        if line.strip().startswith("#"):
            title = line.split("#", 1)[-1].strip()
            if _line_mentions_other(title, others, active_creator):
                continue
            out.append(line)
            continue

        # Drop lines that only exist to name another channel
        cleaned = _clean_comparison_line(line, others)
        if (
            cleaned
            and not _line_mentions_other(cleaned, others, active_creator)
            and len(cleaned) > 15
        ):
            out.append(cleaned)

    result = "\n".join(out)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


# Labels used in SHORTS_MASTER_FRAMEWORK.md per-creator close section
_FRAMEWORK_CREATOR_LABELS: dict[str, list[str]] = {
    "Shivanshu.Agrawal": ["Shivanshu"],
    "GenZway": ["GenZway"],
    "hellooipsita": ["Ipsita"],
    "Finsaheliofficial": ["Finsaheli"],
    "openletteryt": ["OpenLetterYT"],
    "PrabhjotSpeaks": ["PrabhjotSpeaks", "Prabhjot"],
    "KKCreate": ["KKCreate"],
    "MangeshShinde": ["MangeshShinde", "Mangesh"],
    "Nitishrajputshorts": ["Nitish"],
    "TheInformedCitizen": ["TheInformedCitizen", "Informed"],
    "NehaGupta": ["NehaGupta", "Neha"],
    "ThinkSchool_Hindi": ["ThinkSchool"],
    "UditInsights": ["Udit"],
    "AshutoshPratihastAP": ["Ashutosh"],
}


def sanitize_framework_for_creator(text: str, active_creator: str) -> str:
    """Keep 5-phase framework; drop other creators' close-formula bullets."""
    if not text.strip():
        return text

    labels = _FRAMEWORK_CREATOR_LABELS.get(
        active_creator, [active_creator.split(".")[0]]
    )
    out: list[str] = []
    in_close_block = False

    for line in text.splitlines():
        if re.search(r"Per-creator close", line, re.I):
            in_close_block = True
            out.append("**Close formula (this channel only):**")
            continue
        if in_close_block:
            if line.strip().startswith("---") or (
                line.strip().startswith("##") and "close" not in line.lower()
            ):
                in_close_block = False
                out.append(line)
                continue
            if any(f"**{lbl}:**" in line for lbl in labels):
                out.append(
                    re.sub(r"\*\*[^*]+:\*\*", "**This channel:**", line, count=1)
                )
            continue
        if not _line_mentions_other(line, _tokens_for_creator(active_creator), active_creator):
            out.append(line)

    return re.sub(r"\n{3,}", "\n\n", "\n".join(out))


PURE_VOICE_AGENT_RULE = """
## ⛔ PURE VOICE (non-negotiable)
- Write **only** as `{creator}` — never name, compare, or imitate any other YouTube creator or channel.
- Do **not** compare to other channels in the script or DNA audit (traits only).
- Use signature phrases from **this** creator's cheatsheet and transcripts only.
- If tempted to borrow a hook from memory of another channel — pick a different entry from **this** creator's `deep_hooks.md`.
"""
