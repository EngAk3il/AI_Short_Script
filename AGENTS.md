# Antigravity / Cursor — Intelligent script generation

**Default mode: agent intelligence, not Python templates.**

Python only **packages patterns** and **validates** output. You (the agent) do **live research** and write the script.

---

## Quick start (what you tell Antigravity)

```
Prepare and write a viral Short script:
- Creator: GenZway
- Topic: RCB 16000 crore sale — who really profits

Run: python3 prepare.py -c GenZway -t "RCB 16000 crore sale"
Then open the *_BRIEF.md file and follow every step.
```

Or in one message:

> Read `scripts/GenZway/<topic>_BRIEF.md`, do live web research with browser, verify every URL, then write the full production script to the matching `*_dna.md` file.

---

## Your responsibilities (the agent)

| Step | Who | What |
|------|-----|------|
| Ingest transcripts | Human / `ingest.py` | `data/<creator>/.../transcript.txt` |
| Learn hook patterns | Human / `deep_hook_learn.py` | `creator_pattern/<creator>/deep_hooks.md` |
| **Prepare brief** | `prepare.py` | Creates `*_BRIEF.md` + `*_context.md` |
| **Research topic** | **YOU (agent)** | Web search + open articles in browser |
| **Write script** | **YOU (agent)** | Full script with verified references |
| **Validate** | `validate_script.py` | Optional URL/structure check |

### You MUST use intelligence for:

1. **Hook choice** — Match topic to a real entry in `deep_hooks.md`, not a generic opener.
2. **Facts** — Search today’s sources; cross-verify; copy real URLs from the browser.
3. **Voice** — Pull phrasing from real `transcript.txt` samples, not generic Hindi.
4. **Retention** — 5-phase tension from `SHORTS_MASTER_FRAMEWORK.md`.
5. **Honesty** — No invented stats or guessed URLs (see `SCRIPT_RULES.md`).

### You must NOT:

- Fill placeholders without research
- Use "Aaj hum baat karenge", "Hey guys", "Welcome back"
- Paste homepage URLs as sources
- Mark `PRODUCTION READY` without verifying references in browser

---

## Transcripts (avoid IP blocks)

See **`INGEST.md`**. Summary:
```bash
yt-dlp --cookies-from-browser chrome --cookies cookies.txt --skip-download 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
python3 ingest.py -c GenZway --cookies cookies.txt --delay 12
python3 ingest.py -c GenZway --retry-failed --cookies cookies.txt   # after blocks
python3 ingest_status.py -c GenZway
```

---

## Commands

```bash
# 1. Package patterns for the agent (run this, then work in Antigravity)
python3 prepare.py -c UditInsights -t "Your topic here"

# 2. After you write the script
python3 validate_script.py scripts/UditInsights/your_topic_dna.md -c UditInsights

# 3. Check hook library quality
python3 validate_hooks.py UditInsights
```

**Avoid** `python3 generate.py --auto` unless you explicitly want API-only generation without agent research.

---

## Files to read (in order)

1. `scripts/<creator>/<topic>_BRIEF.md` — mission + workflow
2. **`creator_pattern/<creator>/CREATOR_MIND.md`** — tone, mindset, brain
3. `creator_pattern/<creator>/hook_cheatsheet.md`
4. `creator_pattern/<creator>/deep_hooks.md` (find similar videos)
5. `patterns/<creator>/dna.md`
6. `data/<creator>/<video_id>/transcript.txt` (2–3 files)
6. `SCRIPT_RULES.md` + `SHORTS_MASTER_FRAMEWORK.md`

Write output to: `scripts/<creator>/<topic>_dna.md`

---

## Skill

Project skill: `.cursor/skills/viral-shorts-script/SKILL.md` — auto-loaded when generating Shorts scripts in this repo.
