# Creator pattern library

**Read order for script generation (Antigravity / Cursor):**

| Priority | File | Purpose |
|----------|------|---------|
| 1 | `CREATOR_MIND.md` | **Tone, mindset, voice brain** — who they are and how to think |
| 2 | `hook_cheatsheet.md` | 30-second hook formulas + forbidden patterns |
| 3 | `deep_hooks.md` | Per-transcript forensic patterns (pick closest video to topic) |
| 4 | `../patterns/<creator>/dna.md` | Full DNA if present (extra depth) |

```bash
python3 prepare.py -c <Creator> -t "<topic>"
```

Agent must read `CREATOR_MIND.md` before writing any script.

## Update deep_hooks after new transcripts

```bash
python3 deep_hook_status.py                    # check coverage %
python3 deep_hook_learn.py Shivanshu.Agrawal   # add missing video_ids only
python3 deep_hook_learn.py --all GenZway       # full rebuild one creator
python3 deep_hook_learn.py --llm --cheatsheet UditInsights  # optional Claude enrich
```

Each `deep_hooks.md` entry uses **real `video_id`** (one row per `transcript.txt`).
