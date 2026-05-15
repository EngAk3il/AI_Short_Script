"""Build intelligence briefs for Antigravity/Cursor — no static script generation."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from lib.generation_context import GenerationContext, _read_optional
from lib.hook_excerpt import excerpt_deep_hooks
from lib.paths import SCRIPTS_DIR
from lib.transcript_format import format_instructions_for_bundle
from lib.voice_purity import PURE_VOICE_AGENT_RULE


def slugify(text: str) -> str:
    out = []
    for ch in text.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in " -_":
            out.append("_")
    s = "".join(out).strip("_")
    while "__" in s:
        s = s.replace("__", "_")
    return s[:80] or "script"


def build_mission_brief(
    ctx: GenerationContext,
    output_script: Path,
    bundle_path: Path,
) -> str:
    """Agent-facing brief: research + write. Voice DNA lives ONLY in context file."""
    slug = bundle_path.name.replace("_context.md", "")

    return f"""# 🧠 AGENT MISSION BRIEF
> **Do not treat this file as the final script.** Live research + write in **pure `{ctx.creator}` voice**.
> Generated: {datetime.now(timezone.utc).isoformat()}

## Assignment
| Field | Value |
|-------|-------|
| **Creator** | `{ctx.creator}` |
| **Topic** | {ctx.topic} |
| **Output script** | `{output_script}` |
| **Context file (ONLY voice source)** | `{bundle_path}` |

---

## ⛔ INPUT RULE — READ THIS FIRST

When writing the script you may open **ONLY**:

1. **`{bundle_path.name}`** — CREATOR_MIND, cheatsheet, DNA, hooks, transcripts, format, rules (everything)
2. **This brief** — workflow + research steps
3. **The web/browser** — verify facts and reference URLs only

**Do NOT open:** `creator_pattern/`, `patterns/`, `data/`, `SCRIPT_RULES.md`, `SHORTS_MASTER_FRAMEWORK.md`, or other creators' scripts.  
If voice guidance is missing from the context file, run `python3 prepare.py -c {ctx.creator} -t "{ctx.topic}"` to rebuild it.

{PURE_VOICE_AGENT_RULE.format(creator=ctx.creator)}

---

## ⚡ Workflow (in order)

### Phase A — Absorb voice (context file only) — **read `CREATOR_SCRIPT_INTELLIGENCE.md` first**
1. Open **Reference transcript** in `{bundle_path.name}` — note **date count in speech** (often **zero**).
2. Read that transcript **aloud** once; count segments and words per line — **match both**.
3. Pick hook from **Topic-matched hooks** — adapt **EXACT HOOK** rhythm (do not write wire copy like `14 May 2026 ko...`).
4. Copy connectors **only if reference uses them** (e.g. Niharika: `Aakhir kya`; Informed Citizen geo: `दोस्तों`; Neha: `Kya aap jaante hain`).

### Phase B — Live research (web only — for facts/URLs, NOT tone)
1. Search topic + verify claims in **≥3 articles**.
2. Dates go in **references table** and **at most once** in spoken script unless reference uses more.
3. Copy **full article URLs** from the address bar.
4. Unverifiable claims → omit or `[UNVERIFIED]`.

### Phase C — Write script (intelligence, not templates)
- Write `[00:00]` lines in the **same shape** as the reference transcript analysis block.
- **Tone from transcript**; **facts from articles** — never paste headline Hindi as the hook.
- Do **not** repeat the same calendar date in multiple lines.
- 5-phase retention inside the reference rhythm (not a generic table).

### Phase D — Self-audit
- [ ] `reference_video` ID named; opening mimics reference pattern
- [ ] Date density ≤ reference (usually 0–1 in speech)
- [ ] Hook adapted from a **Topic-matched hooks** EXACT HOOK (quote first words in audit)
- [ ] Phrases used appear in reference OR CREATOR_MIND (no borrowed creator-isms)
- [ ] References table with verified full URLs
- [ ] Run: `python3 validate_script.py "{output_script}" -c {ctx.creator}`

---

## After you finish
1. Save full script to: **`{output_script}`**
2. Set `Status: PRODUCTION READY` only after URL + voice check
3. Remove any "AWAITING AGENT" placeholder text
"""


def build_context_bundle(ctx: GenerationContext) -> str:
    """Single file with ALL voice + format context for script generation."""
    hooks_excerpt = excerpt_deep_hooks(ctx.deep_hooks, ctx.topic)
    samples_block = (
        "\n\n---\n\n".join(ctx.samples[:5])
        if ctx.samples
        else "(no transcripts ingested — rely on cheatsheet)"
    )

    parts = [
        f"# Context bundle: {ctx.creator}\n",
        f"Topic: {ctx.topic}\n",
        "> **Agents:** Use ONLY this file + `*_BRIEF.md` for voice. Do not open creator_pattern/ or data/.\n",
        "\n## CREATOR MIND\n",
        ctx.creator_mind or "(none)",
        "\n## Hook cheatsheet\n",
        ctx.hook_cheatsheet or "(none)",
        f"\n{hooks_excerpt}\n",
        "\n## DNA (patterns/dna.md)\n",
        ctx.dna_md or "(none)",
        "\n## Transcript samples (COPY RHYTHM FROM THESE)\n",
        samples_block,
        "\n## Retention framework (this channel only)\n",
        ctx.framework[:3500],
        "\n## Script rules\n",
        ctx.script_rules[:2500],
        "\n## Intelligence guide (mandatory)\n",
        _read_optional(Path(__file__).resolve().parent.parent / "CREATOR_SCRIPT_INTELLIGENCE.md", 4000),
        format_instructions_for_bundle(ctx.creator, ctx.topic),
    ]
    return "\n".join(parts)


def write_agent_package(ctx: GenerationContext) -> dict[str, Path]:
    """Write brief + context bundle + empty script target path. Returns paths."""
    out_dir = SCRIPTS_DIR / ctx.creator
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(ctx.topic)
    script_path = out_dir / f"{slug}_dna.md"
    brief_path = out_dir / f"{slug}_BRIEF.md"
    bundle_path = out_dir / f"{slug}_context.md"

    bundle_path.write_text(build_context_bundle(ctx), encoding="utf-8")
    brief_path.write_text(
        build_mission_brief(ctx, script_path, bundle_path),
        encoding="utf-8",
    )

    if not script_path.exists() or "AWAITING AGENT" in script_path.read_text(
        encoding="utf-8"
    ):
        script_path.write_text(
            f"# Script: {ctx.topic}\n"
            f"# Creator: {ctx.creator}\n"
            f"# Status: AWAITING AGENT\n\n"
            f"Read `{brief_path.name}` and `{bundle_path.name}` ONLY — then write full script here.\n",
            encoding="utf-8",
        )

    return {
        "brief": brief_path,
        "bundle": bundle_path,
        "script": script_path,
    }
