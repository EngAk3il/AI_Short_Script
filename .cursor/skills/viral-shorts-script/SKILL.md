---
name: viral-shorts-script
description: >-
  Generate verified, high-retention YouTube Shorts scripts for Indian creators in
  AI_Short_Script. Use when the user asks for a script, topic, Antigravity generation,
  viral shorts, creator DNA, or mentions prepare.py / generate.py / creator patterns.
---

# Viral Shorts Script (Intelligence-First)

## Core principle

**You write the script. Python does not.**

- Run `python3 prepare.py -c <Creator> -t "<topic>"` to create `*_BRIEF.md`.
- Follow the brief: **live web research** → **read real transcripts** → **write** → **validate**.

Never output generic "Aaj hum baat karenge" openings. Never invent URLs or statistics.

---

## Workflow

### 1. Prepare (if brief missing)

```bash
python3 prepare.py -c <Creator> -t "<topic>"
```

Open `scripts/<Creator>/<slug>_BRIEF.md`.

### 2. Research (mandatory — use browser + web search)

- Search topic + India + 2025/2026 dates.
- Open **≥3 reputable articles**; read claims on-page.
- Cross-check big numbers with a second source.
- Copy **full article URLs** from the address bar (not homepages).
- If unverifiable → omit or `[UNVERIFIED — needs manual check]`.

Trusted: LiveMint, Economic Times, Moneycontrol, Reuters, The Hindu, official company/gov sites.

### 3. Learn voice (read files IN ORDER — do not guess)

| # | File | Purpose |
|---|------|---------|
| 1 | `creator_pattern/<C>/CREATOR_MIND.md` | **Mindset, tone, arc, NEVER rules** |
| 2 | `creator_pattern/<C>/hook_cheatsheet.md` | Hook templates, CTA |
| 3 | `creator_pattern/<C>/deep_hooks.md` | Per-video patterns — closest match to topic |
| 4 | `patterns/<C>/dna.md` | Extra voice evidence |
| 5 | `data/<C>/<video_id>/transcript.txt` | Real rhythm and phrases |

### 4. Write for retention

Use `SHORTS_MASTER_FRAMEWORK.md`:

- **STOP (0–5s):** tension, paradox, number shock — not intro filler
- **TRAP → BUILD → TWIST → CLOSE**
- Include **WATCH-THROUGH MAP** and **DNA Adherence Audit**
- End with creator's real CTA style from cheatsheet

### 5. References table (mandatory)

```markdown
### 📚 References & Sources
| # | Data Point Used | Source | Link |
```

Every stat in the script must appear here with a **verified full article URL**.

### 6. Validate

```bash
python3 validate_script.py scripts/<Creator>/<file>_dna.md -c <Creator>
```

Fix all failures before setting `Status: PRODUCTION READY`.

---

## Output location

Write the complete script to the path named in `*_BRIEF.md` (usually `scripts/<Creator>/<slug>_dna.md`).

Remove "AWAITING AGENT" / placeholder text.

---

## Quality bar

- Hook type named + tied to a real `deep_hooks.md` entry
- 3+ signature phrases from cheatsheet
- 8+ timestamp rows or clear phase sections
- Zero hallucinated facts
- Reads like the **creator**, not a generic AI narrator
