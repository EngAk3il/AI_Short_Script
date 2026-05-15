"""Build intelligence briefs for Antigravity/Cursor — no static script generation."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from lib.generation_context import GenerationContext
from lib.paths import SCRIPTS_DIR


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


def build_mission_brief(ctx: GenerationContext, output_script: Path) -> str:
    """Agent-facing brief: research + write. Python does NOT write the script body."""
    samples_preview = ""
    for i, s in enumerate(ctx.samples[:3], 1):
        samples_preview += f"\n### Sample {i}\n{s[:1200]}\n...(truncated in brief — read full file in data/)\n"

    mind_block = ctx.creator_mind or (
        f"⚠️ Missing `creator_pattern/{ctx.creator}/CREATOR_MIND.md` — read deep_hooks + dna.md carefully"
    )
    cheatsheet = ctx.hook_cheatsheet or f"(see CREATOR_MIND.md + deep_hooks.md)"
    hooks_note = (
        f"Per-transcript library: `creator_pattern/{ctx.creator}/deep_hooks.md` "
        f"({len(ctx.deep_hooks)} chars)"
    )

    return f"""# 🧠 AGENT MISSION BRIEF
> **Do not treat this file as the final script.** Your job is live research + intelligent writing.
> Generated: {datetime.now(timezone.utc).isoformat()}

## Assignment
| Field | Value |
|-------|-------|
| **Creator** | `{ctx.creator}` |
| **Topic** | {ctx.topic} |
| **Output script** | `{output_script}` |
| **Voice** | {ctx.creator_bio} |

---

## ⚡ Intelligence workflow (MANDATORY — in order)

You are **not** filling a template from memory. You are an investigative scriptwriter.

### Phase A — Become the creator (read files IN ORDER)
1. **`creator_pattern/{ctx.creator}/CREATOR_MIND.md`** — adopt mindset, tone, emotional arc (THIS IS YOUR BRAIN).
2. `hook_cheatsheet.md` — pick hook **type** (rotate from last script).
3. `deep_hooks.md` — find 2–3 **real transcript entries** closest to this topic; mirror EXACT patterns.
4. `patterns/{ctx.creator}/dna.md` if present — extra voice evidence.
4. Read 2–3 full `data/{ctx.creator}/<video_id>/transcript.txt` files (best match to topic) — absorb rhythm and vocabulary.
5. Read `SCRIPT_RULES.md` and `SHORTS_MASTER_FRAMEWORK.md` — retention + zero hallucination.

### Phase B — Live research (browser + web — NOT guesses)
1. **Search the web** for the topic + India context + recent dates.
2. Open **at least 3 independent reputable sources** (LiveMint, ET, Moneycontrol, Reuters, official filings, etc.).
3. For **every statistic, name, date, ₹ figure** in the script:
   - Confirm on the page (read it, don't trust snippet alone).
   - Copy the **exact URL from the address bar** after the page loads.
   - Cross-check with a **second source** when possible.
4. If a claim cannot be verified → **omit it** or mark `[UNVERIFIED — needs manual check]` — never invent URLs.
5. Reject homepage-only links (`https://livemint.com/`). Use full article paths only.

### Phase C — Write for retention (viral = unresolved tension)
Apply 5-phase structure from `SHORTS_MASTER_FRAMEWORK.md`:
- **0–5s STOP** — ego challenge, paradox, number shock, or betrayal. **Never** "Aaj hum baat karenge" / "Hey guys".
- **5–20s TRAP** — partial info; viewer must stay for the answer.
- **20–45s BUILD** — stacked verified facts (fast/slow pacing alternation).
- **45–60s TWIST** — real insight or villain reveal.
- **60–80s CLOSE** — creator's exact CTA style from cheatsheet.

### Phase D — Self-audit before saving
- [ ] Opening matches a **documented hook formula** from deep_hooks (cite which #entry you mirrored)
- [ ] 3+ signature vocabulary items from cheatsheet appear naturally
- [ ] No forbidden patterns for this creator
- [ ] Every number in script appears in References table with **working full URL**
- [ ] `## Status: PRODUCTION READY` only if you personally verified every reference in browser
- [ ] Run: `python3 validate_script.py "{output_script}" -c {ctx.creator}` and fix failures

---

## CREATOR MIND (tone & brain — internalize before writing)

{mind_block[:8000]}

---

## Hook cheatsheet (quick reference)

{cheatsheet[:4000]}

{hooks_note}

---

## Transcript voice samples (preview)

{samples_preview or "⚠️ No samples found — ingest transcripts first."}

---

## DNA file
{"Read: `patterns/" + ctx.creator + "/dna.md`" if ctx.dna_md else "⚠️ No dna.md — rely on deep_hooks + transcripts."}

---

## Output format (write to `{output_script}`)

```markdown
# 🎬 MASTER PRODUCTION SCRIPT
## Topic: {ctx.topic}
## Creator: {ctx.creator}
## Hook Type: [from library — name + which deep_hooks #entry inspired it]
## Duration: ~60-90s
## Status: PRODUCTION READY

## WHY THIS SCRIPT WORKS
(retention curve: 0s / 10s / 25s / 45s / 60s)

## FULL SCRIPT
| Timestamp | Script | Note |
|-----------|--------|------|
| [00:00] | ... | PHASE 1 STOP |
... (8+ rows) ...

## WATCH-THROUGH MAP
...

### DNA Adherence Audit
- Hook formula used: ...
- Signature tics: ...
- Forbidden patterns avoided: ...
- CTA: ...

### 📚 References & Sources
| # | Data Point Used | Source | Link |
|---|----------------|--------|------|
| 1 | ... | ... | [full verified article URL] |
```

---

## After you finish
1. Save the complete script to: **`{output_script}`**
2. Delete any "Pending generation" placeholder text.
3. Optional check: `python3 validate_script.py "{output_script}" -c {ctx.creator}`
"""


def build_context_bundle(ctx: GenerationContext) -> str:
    """Single file the agent can @-mention with essential pattern context."""
    parts = [
        f"# Context bundle: {ctx.creator}\n",
        f"Topic: {ctx.topic}\n",
        "## CREATOR MIND (read first)\n",
        ctx.creator_mind or "(none)",
        "\n## Hook cheatsheet\n",
        ctx.hook_cheatsheet or "(none)",
        "\n## DNA (patterns/dna.md)\n",
        ctx.dna_md or "(none)",
        "\n## Framework excerpt\n",
        ctx.framework[:4000],
        "\n## Script rules excerpt\n",
        ctx.script_rules[:3000],
    ]
    if ctx.samples:
        parts.append("\n## Top transcript samples\n")
        parts.append("\n---\n".join(ctx.samples[:3]))
    return "\n".join(parts)


def write_agent_package(ctx: GenerationContext) -> dict[str, Path]:
    """Write brief + context bundle + empty script target path. Returns paths."""
    out_dir = SCRIPTS_DIR / ctx.creator
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(ctx.topic)
    script_path = out_dir / f"{slug}_dna.md"
    brief_path = out_dir / f"{slug}_BRIEF.md"
    bundle_path = out_dir / f"{slug}_context.md"

    brief_path.write_text(build_mission_brief(ctx, script_path), encoding="utf-8")
    bundle_path.write_text(build_context_bundle(ctx), encoding="utf-8")

    if not script_path.exists() or "Pending generation" in script_path.read_text(encoding="utf-8"):
        script_path.write_text(
            f"# Script: {ctx.topic}\n"
            f"# Creator: {ctx.creator}\n"
            f"# Status: AWAITING AGENT — read `{brief_path.name}` and write full script here\n\n"
            f"👉 Antigravity: Open `{brief_path.name}` and follow the intelligence workflow.\n",
            encoding="utf-8",
        )

    return {
        "brief": brief_path,
        "bundle": bundle_path,
        "script": script_path,
    }
