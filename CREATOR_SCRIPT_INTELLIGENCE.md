# Creator script intelligence (read before writing any `*_dna.md`)

> **Coding cannot write the script.** `prepare.py` only packages transcripts and rules.  
> **You** must read, hear, and imitate one real video — then write.

---

## Why scripts sounded fake (root causes)

1. **Wrong phrases stuffed in** — e.g. forcing `Dar-asal` / `Aaiye samajhte hain` on The Informed Citizen when their geo Shorts open with **`दोस्तों, [state] की geography...`** (see `data/TheInformedCitizen/TsiWJSld98s/transcript.txt`).
2. **Date spam** — User JSON had `2026-05-14`; agents repeated it every line. **Real Niharika/Neha transcripts almost never say years or "May 14" in speech.** Dates belong in the references table, not in every beat.
3. **News-anchor Hindi** — Generic "14 May ko SC ne..." instead of that creator's hook from `deep_hooks.md` (verbatim rhythm).
4. **Same skeleton for everyone** — Markdown tables copied from Shivanshu onto Neha/Niharika.

---

## The only workflow that works

### Step 1 — Pick ONE reference video (from context bundle)

Open `*_context.md` → **Reference transcript** section.  
That video was chosen by topic overlap + archetype. **Do not switch to a table format from another creator.**

### Step 2 — Read the reference like a director

Count in the reference:

| Check | Action |
|-------|--------|
| How many `[00:00]` lines? | Write the **same count** (±1). |
| Words per line? | Short (8–15) vs long (25–40) — **match**. |
| Dates in speech? | If **0**, you get **max 1 date** in full script. |
| Opening words? | Copy **pattern** (question / दोस्तों / Kya aap jaante / Aakhir kya). |
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

---

## Per-creator voice (from real transcripts, not guesses)

### NiharikaChoudhary

- **Sounds like:** passionate civic friend; `Aakhir kya hua/thi`; `Aap khud sochiye`; `Aap kya sochte hain`.
- **Rarely:** calendar dates in every line; "Simple words mein" every video (use when explaining law).
- **Hooks:** injustice, question, contrast — see `creator_pattern/NiharikaChoudhary/deep_hooks.md`.
- **Reference examples:** `8EEqmu6MVwY` (legal term → danger), `7FHRhFFa28I` (Aakhir kya hua scam).

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
