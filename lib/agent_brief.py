"""Build intelligence briefs for Antigravity/Cursor — no static script generation."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from lib.generation_context import GenerationContext
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

### Phase A — Absorb voice (context file only)
1. Read **`{bundle_path.name}`** top to bottom once.
2. Pick hook type from **Hook cheatsheet** + **Topic-matched hooks** section.
3. Copy rhythm from **Transcript samples** — sentence length, connectors, CTA style.
4. Read **REQUIRED FORMAT** at bottom of context — match the **named reference video** structure (usually `[00:00]` prose, not a generic table).

### Phase B — Live research (web only — for facts/URLs)
1. Search topic + India + 2026 dates.
2. Open **≥3 reputable articles**; confirm every stat on-page.
3. Copy **full article URLs** from the address bar.
4. Unverifiable claims → omit or `[UNVERIFIED]`.

### Phase C — Write script
- Match **REQUIRED FORMAT** exactly — copy the **matched reference transcript** shape from context.
- Mirror transcript **rhythm** (line length, connectors like `Aakhir kya hua` / `Dar-asal`), not generic news Hindi.
- 5-phase retention: STOP → TRAP → BUILD → TWIST → CLOSE.

### Phase D — Self-audit
- [ ] Structure matches REQUIRED FORMAT + reference video named in audit
- [ ] ≥3 signature phrases from context cheatsheet (natural, not stuffed)
- [ ] Copied CTA **verbatim** where context specifies exact wording
- [ ] Hook tied to a topic-matched hook entry (name it in metadata)
- [ ] No other creator/channel names anywhere
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
