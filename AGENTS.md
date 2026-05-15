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
4. **Structure** — Copy the **matched reference video** in `*_context.md` (usually `[00:00]` prose). **Never paste the same table layout for every creator** (see `SCRIPT_RULES.md` Rule 2b).
5. **Retention** — 5-phase tension from `SHORTS_MASTER_FRAMEWORK.md`.
6. **Honesty** — No invented stats or guessed URLs (see `SCRIPT_RULES.md`).

### You must NOT:

- Fill placeholders without research
- Use "Aaj hum baat karenge", "Hey guys", "Welcome back"
- Paste homepage URLs as sources
- Mark `PRODUCTION READY` without verifying references in browser
- **Name or imitate other creators** (e.g. "not GenZway style") — use trait-only rules from **this** creator's files only

After updating pattern files, run `python3 sanitize_voice_patterns.py` and re-run `prepare.py` so `*_context.md` stays pure.

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

## Files to read when writing a script

**ONLY these two** (voice + format is bundled inside context):

1. `scripts/<creator>/<topic>_BRIEF.md` — workflow + research steps  
2. `scripts/<creator>/<topic>_context.md` — CREATOR_MIND, hooks, transcripts, REQUIRED FORMAT  

Plus **live web** for verified facts/URLs only.

Do **not** open `creator_pattern/`, `patterns/`, or `data/` during script generation.

Write output to: `scripts/<creator>/<topic>_dna.md`

After pipeline changes: `python3 prepare.py -c <Creator> -t "<topic>"` then validate with `python3 validate_script.py ...`

---

## Skill

Project skill: `.cursor/skills/viral-shorts-script/SKILL.md` — auto-loaded when generating Shorts scripts in this repo.
