# Creator script intelligence (read before writing any `*_dna.md`)

> **Coding cannot write the script.** `prepare.py` only packages transcripts and rules.  
> **You** must read, hear, and imitate one real video — then write.

---

## Why scripts sounded fake (root causes)

1. **Wrong phrases stuffed in** — e.g. forcing `Dar-asal` / `Aaiye samajhte hain` on The Informed Citizen when their geo Shorts open with **`दोस्तों, [state] की geography...`** (see `data/TheInformedCitizen/TsiWJSld98s/transcript.txt`).
2. **Date spam** — User JSON had `2026-05-14`; agents repeated it every line. **Real Niharika/Neha transcripts almost never say years or "May 14" in speech.** Dates belong in the references table, not in every beat.
3. **News-anchor Hindi** — Generic "14 May ko SC ne..." instead of that creator's hook from `deep_hooks.md` (verbatim rhythm).
4. **Pure Devanagari script walls** — Writing full script in Devanagari when on-camera delivery is **Romanized Hinglish** (`Tirupati mein Gangamma...`, `matlab`, `lekin`). Ingest may be Devanagari; **output is still Romanized** unless context explicitly requires Devanagari.
5. **Too short (<2 min)** — 8–11 beats / 70–90s feels rushed; target **≥120s spoken**, **≥360 words**, last stamp **`[01:55]`+**.
6. **Wrong reference + fake mapping** — Citing `6-JWJUVkuPg` (Ramnami) for Gangamma while the opener is generic English news.
7. **Same skeleton for everyone** — Markdown tables copied from Shivanshu onto Neha/Niharika.

---

## The only workflow that works

### Step 1 — Pick ONE reference video (from context bundle)

Open `*_context.md` → **Reference transcript** section.  
That video was chosen by topic overlap + archetype. **Do not switch to a table format from another creator.**

### Step 2 — Read the reference like a director

Count in the reference:

| Check | Action |
|-------|--------|
| How many `[00:00]` lines? | **≥14** for explainers (2 min); or reference count ±1 if reference is already long. |
| Total words (FULL SCRIPT)? | **≥360** Romanized words (≥320 for slow WPS creators). |
| Last timestamp? | **`[01:55]` minimum** — prefer `[02:00]+`. |
| Words per line? | Short (8–15) vs long (25–45) — **match reference density**. |
| Dates in speech? | If **0**, you get **max 1 date** in full script. |
| Opening words? | Copy **pattern** in **Romanized Hinglish** (question / doston / kya aap jaante / aakhir kya / ne is tarah se / yeh ___ hai). |
| Script alphabet? | **Romanized default** — brands/tickers in English OK. Devanagari only if context mandates. |
| CTA? | Copy **type** (comment state name / follow / no subscribe). |

### Step 3 — Hook from `deep_hooks.md`, not from headlines

- Find **Topic-matched hooks** in context.
- Adapt **EXACT HOOK** rhythm — same sentence shape, new facts.
- **Bad:** `14 May 2026 ko Supreme Court ne...` (wire copy)  
- **Good (Niharika legal):** `Electoral bonds — jise transparent bola gaya tha, lekin SC ne...` → adapt to Unnao order.

### Step 4 — Facts from browser; tone from transcript

- Stats, names, court orders → **verified articles** → references table.
- **Never** pull tone from The Hindu's English headline.
- If a fact needs a date, say it **once** naturally: `is hafte SC ne...` or `kal ki hearing mein...`

### Step 5 — DNA audit must prove imitation

```markdown
- Structure matched: `<video_id>` — opening mimics "<first 8 words of reference>"
- Dates in speech: 0 (matched reference) / 1 (only for X)
- Hook adapted from deep_hooks entry: "<EXACT HOOK first line...>"
- Did NOT use: [phrases this creator never says]
```

### Step 6 — Mechanism vs headline (why viewers stay)

**Shivanshu reference transcripts (e.g. `y7qQ3N40Flc`) teach HOW things work** — `जब रिफाइनरी में... तो... इसीलिए... लेकिन...` — not a list of news numbers.

| Bad (user scrolls) | Good (user stays) |
|--------------------|-------------------|
| "₹500 करोड़ नुकसान, pool ₹1.98 लाख करोड़, ICRA hike" | "जब क्रूड ऊपर और पंप कीमत पीछे → हर लीटर घाटा → ₹3 के बाद भी ₹500 करोड़/दिन" |
| Facts without one taught chain | Each `[00:00]` line answers the **previous** open question |
| English labels: wallet, structural, retail | Hindi: जेब, असलियत, पंप |

**WATCH-THROUGH MAP must include column: `Viewer question (why they stay)`** — one unresolved question per phase until CLOSE.

**Shivanshu.Agrawal:** After hook, start mechanism in **same breath** as reference (`facts surprise kar denge — jab...`). Target **≥14** beats and **≥2:00** for explainers; **long Romanized lines** where reference has long lines.

**All creators (default):** `## FULL SCRIPT` = **Romanized Hinglish**. Minimum **120 seconds** spoken — see `SCRIPT_RULES.md` Rule **2h**.

### Agent pre-flight (copy before marking PRODUCTION READY)

```
□ Read full reference transcript.txt aloud once
□ [00:00] same DEVICE as reference (not topic headline in English)
□ Script teaches ONE chain / list / case — not 4 unlinked stats
□ WATCH-THROUGH: every phase has "Viewer question (why they stay)"
□ DNA audit quotes: Opening mimics: "..." → "..."
□ validate_script.py passed
```

**If any box fails → rewrite FULL SCRIPT, do not patch the hook only.**

### Step 7 — Viral flow (why scripts still feel “AI” after structure passes)

Structure (HOOK PATTERN, viewer column) is **not** enough. Read the reference `transcript.txt` **aloud** and match **pacing + connectors**, not just topic.

| Transcript signal | Copy in script | Do NOT |
|-------------------|----------------|--------|
| Shivanshu `ने इस तरह से` / `फैक्ट्स सरप्राइज़` | Named brand/person + shock in line 1; chain with `और इसीलिए`, `आल्सो`, `फाइनली` | CAC, AOV, analyst, essay paragraphs |
| Shivanshu LPG (`y7qQ3N40Flc`) | `जब…` starts in **same breath** as hook; long process lines | Stat stack without process |
| Niharika bonds (`8EEqmu6MVwY`) | `…लेकिन SC…` then **own beat**: `आखिर क्या था?` | Legal English wall in hook |
| TheInformedCitizen (`MV0iICFivJk`) | **6s beats**: question → सीधा असर → fact | 30-word single `[00:00]` |
| TheInformedCitizen (`o5JD2kPJBig`) | `सबसे बड़ी गलती:` punch → `लेकिन` at ~6s | Soft geography essay |
| KKCreate (`8Mpwirtw01g`) | Superlative → list escalates → vox-pop Q | One-line ritual dump |
| Prabhjot (`BYuiFKs77GU`) | 2–4s micro-beats; `लेकिन` **alone on a line** sometimes | Long digest sentences |
| ThinkSchool | `बिज़नेस लैब` / insight + `लेकिन` + `कॉस्ट ऑफ फेलियर` | Macro headline stack only |

**Wrong reference = wrong flow.** Example: D2C bleed → use `M8YJZSI5xTw` (ने इस तरह से + gap) + `QHBw621YmC8` (`लेकिन एक प्रॉब्लम थी`), not only a generic news hook.

**Gold listen-test:** If the script sounds like a blog post read aloud, rewrite. If it sounds like one breath rushing to the next fact, it’s closer.

---

## Per-creator voice (from real transcripts, not guesses)

### NiharikaChoudhary

- **Sounds like:** passionate civic friend; `Aakhir kya hua/thi`; `Aap khud sochiye`; `Aap kya sochte hain`.
- **Rarely:** calendar dates in every line; "Simple words mein" every video (use when explaining law).
- **Hooks:** injustice, question, contrast — see `creator_pattern/NiharikaChoudhary/deep_hooks.md`.
- **Reference examples:** `8EEqmu6MVwY` (legal term → danger), `7FHRhFFa28I` (Aakhir kya hua scam).

**Timestamp + density (mandatory for Niharika):**

| Wrong | Right (from `Jp4QTu9GAQg`, `2NfOAbs9xd8`, `-MPsKmt903A`) |
|-------|-------------------------------------------------------------|
| 5–6 beats in 40s | **8–10 beats in 60–75s** |
| `[00:00]` then `[00:24]` (16s gap) | **~7–8s gaps** between beats (6s for IDFC-style short refs only) |
| 1 fact per line | **2–3 facts per beat** (names, numbers, dates, institutions) |
| `आखिर क्या` inside a paragraph | **Own line** after hook: `[00:08] आखिर क्या था/बदला?` |
| Short ref `8EEqmu6MVwY` (15s) as pacing model | Use it for **hook device only**; pace from **`Jp4QTu9GAQg`** (65s, 10 beats) |

Before `PRODUCTION READY`: add **Timestamp cadence** table; read script aloud — total time **≥2:00** for explainers (Niharika included).

### TheInformedCitizen

- **Geo/map Shorts:** `दोस्तों, [X] की geography...` → regions on map → comment which state next → follow.
- **Policy/news:** `Seedha matlab aapke liye`, `Background mein samajhna zaroori hai` — **CREATOR_MIND**, not random "Dar-asal".
- **Avoid:** stuffing phrases this channel doesn't use in the matched reference.
- **Reference examples:** `TsiWJSld98s` (Bihar geo), `-49kHynjprk` (Red gold question), `FO2JWEO1BrQ` (long domino story).

### NehaGupta

- **Sounds like:** warm heritage host; lists of places; `Kya aap jaante hain`; `darshan`; `hamari sanskriti`; `Comment mein...`.
- **Avoid:** political attack, fuel prices, court drama, breaking-news dates.
- **Rarely:** years in speech — festivals = place names + scale, not "May 11-14, 2026" every line.
- **Reference examples:** `hxWwtztLxLY` (temple list), `qp_ptIZBdy0` (bindi regional discovery).

---

## Anti-patterns (instant fail)

| Don't | Do instead |
|-------|------------|
| `14 May 2026` in 4+ lines | Once or zero; use `abhi` / `is order mein` |
| Shivanshu 4-column table on Neha | `[00:00]` lines like her reference |
| Invent hooks not in deep_hooks | Adapt a listed EXACT HOOK |
| Copy another creator's CTA | Use reference video's close |
| Mark PRODUCTION READY without reading reference | Read reference aloud once |

---

## After writing

```bash
python3 validate_script.py scripts/<Creator>/<file>_dna.md -c <Creator>
```

Validation checks URLs — **you** check voice by re-reading the reference transcript side-by-side.
