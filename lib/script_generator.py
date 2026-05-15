"""LLM script generation with validation and retry."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from anthropic import Anthropic

from lib.generation_context import GenerationContext
from lib.reference_validator import validate_references
from lib.research import format_facts_for_prompt
from lib.script_validator import validate_script

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
MAX_RETRIES = 2


def _client() -> Anthropic:
    return Anthropic()


def build_generation_prompt(
    ctx: GenerationContext,
    retry_feedback: str = "",
) -> str:
    samples_block = "\n\n---\n".join(ctx.samples[:5]) if ctx.samples else "No samples."
    facts_block = format_facts_for_prompt(ctx.facts) if ctx.facts else "{}"
    dna_block = ctx.dna_md or "(No patterns/dna.md — use hook library only)"

    retry_section = ""
    if retry_feedback:
        retry_section = f"\n\n=== FIX THESE ISSUES FROM LAST ATTEMPT ===\n{retry_feedback}\n"

    return f"""You are writing a PRODUCTION-READY YouTube Shorts script.

Creator: {ctx.creator}
Topic: {ctx.topic}
Creator voice: {ctx.creator_bio}

=== RETENTION FRAMEWORK (MANDATORY 5-PHASE) ===
{ctx.framework[:5000]}

=== SCRIPT RULES (ZERO HALLUCINATION) ===
{ctx.script_rules[:4000]}

=== CREATOR DNA (patterns/dna.md) ===
{dna_block}

=== HOOK LIBRARY + PER-TRANSCRIPT PATTERNS ===
{ctx.hooks_for_prompt()}

=== REAL TRANSCRIPT VOICE SAMPLES ===
{samples_block}

=== VERIFIED FACTS & SOURCES (use ONLY these URLs for claims) ===
{facts_block}

=== STRICT REQUIREMENTS ===
1. Pick the best HOOK TYPE from the library for this topic — NOT generic "aaj hum baat karenge".
2. Follow 5-PHASE retention: STOP (0-5s) → TRAP → BUILD → TWIST → CLOSE.
3. Opening line ≤ 10 words where possible; create unresolved tension in second 1.
4. Use creator signature vocabulary from cheatsheet — no cross-contamination.
5. Include specific numbers, names, dates from VERIFIED FACTS only.
6. If a fact is not in verified sources, omit it or mark [UNVERIFIED — needs manual check] — prefer omit.
7. End with creator's exact CTA style from library.

=== OUTPUT FORMAT (complete all sections) ===

# 🎬 MASTER PRODUCTION SCRIPT
## Topic: {ctx.topic}
## Creator: {ctx.creator}
## Hook Type: [NAME FROM LIBRARY]
## Duration: ~60-90 seconds
## Status: PRODUCTION READY

---

## WHY THIS SCRIPT WORKS
Brief retention map: what happens at 0s, 10s, 25s, 45s, 60s (tension curve).

---

## FULL SCRIPT

| Timestamp | Script | Note |
|-----------|--------|------|
| [00:00] | ... | PHASE 1: STOP — hook |
| [00:05] | ... | PHASE 2: TRAP |
| ... at least 8 rows through ~75s ...

---

## WATCH-THROUGH MAP
```
0s → ...
15s → ...
...
```

---

### DNA Adherence Audit:
- Hook formula used: ...
- Signature tics verified: (list exact phrases used)
- Forbidden patterns avoided: (confirm)
- CTA format: ...

---

### 📚 References & Sources:

| # | Data Point Used | Source | Link |
|---|----------------|--------|------|
| 1 | [exact claim] | [publication] | [FULL article URL from verified sources] |

(Minimum 2 rows — every statistic in script must appear here with a working full article URL)

{retry_section}
Write the complete script now."""


def generate_script(
    ctx: GenerationContext,
    retry_feedback: str = "",
) -> str:
    prompt = build_generation_prompt(ctx, retry_feedback)
    response = _client().messages.create(
        model=MODEL,
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def generate_with_validation(ctx: GenerationContext) -> tuple[str, bool, str]:
    """
    Generate script, validate structure + URLs, retry on failure.
    Returns (markdown, passed, log_message).
    """
    feedback = ""
    script = ""
    for attempt in range(1, MAX_RETRIES + 2):
        script = generate_script(ctx, feedback)
        script_val = validate_script(script, ctx.creator)
        ref_val = validate_references(script)

        if script_val.passed and ref_val.passed:
            header = (
                f"<!-- Generated: {datetime.now(timezone.utc).isoformat()} -->\n"
                f"<!-- Model: {MODEL} -->\n"
                f"<!-- Validation: PASSED -->\n\n"
            )
            return header + script, True, "Validation passed"

        feedback = script_val.feedback_for_retry()
        if ref_val.errors:
            feedback += "\n" + "\n".join(ref_val.errors)
        feedback += "\nEnsure References table has full article URLs that were in verified_sources."

    return script, False, f"Validation failed after retries:\n{feedback}"
