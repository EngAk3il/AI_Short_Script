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

**Pure voice:** Never name or compare other YouTube creators/channels in the script, audit, or hooks. Only use the assigned creator's `CREATOR_MIND.md`, cheatsheet, and transcripts.

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

### 3. Learn voice (ONLY from prepared bundle)

| # | File | Purpose |
|---|------|---------|
| 1 | `scripts/<C>/<topic>_context.md` | **Everything:** mind, cheatsheet, hooks, transcripts, format |
| 2 | `scripts/<C>/<topic>_BRIEF.md` | Workflow + research rules |

Do **not** open `creator_pattern/`, `patterns/`, or `data/` — samples are already inside `*_context.md`.

### 4. Match transcript structure (before writing)

In `*_context.md`, scroll to **REQUIRED FORMAT (from real transcript)**:

- Note **Matched archetype** + **reference video ID**
- Read the **reference transcript excerpt** — mirror its shape (`[00:00]` lines, domino chain, temple list, etc.)
- **Do not** default to a 4-column markdown table for all creators

### 5. Write for retention

- **STOP (0–5s):** tension, paradox, number shock — not intro filler
- **TRAP → BUILD → TWIST → CLOSE**
- Include **WATCH-THROUGH MAP** and **DNA Adherence Audit** (name reference video ID)
- End with creator's real CTA style from cheatsheet

### 6. References table (mandatory)

```markdown
### 📚 References & Sources
| # | Data Point Used | Source | Link |
```

Every stat in the script must appear here with a **verified full article URL**.

### 7. Validate

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
- 6+ `[00:00]` lines OR creator-native structure from reference transcript (not a copied cross-creator table)
- Zero hallucinated facts
- Reads like the **creator**, not a generic AI narrator
