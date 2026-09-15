# Script Generation Rules 📋

> These rules MUST be followed for EVERY script generated in this system.
> Last updated: 2026-05-15

## Rule 0: ZERO HALLUCINATION (ABSOLUTE)

> [!CAUTION]
> **NEVER fabricate, guess, or construct URLs, data points, statistics, or facts.**
> If you cannot find a verified source for a data point, say so explicitly.
> Getting something wrong wastes real human effort and breaks trust.

### What counts as hallucination:
- **Constructing URLs** by guessing the path pattern (e.g. `/article-slug-123.html`)
- **Inventing statistics** not backed by a verifiable source
- **Guessing institution names** (e.g. saying "IIT" when it's actually "IISc")
- **Making up article titles** or publication names
- **Assuming URL structures** for websites you haven't visited

### What you MUST do instead:
1. **Search the web** for the actual data point
2. **Click through** to the actual article in the browser
3. **Copy the exact URL** from the address bar after confirming the page loads
4. If a URL cannot be verified, **DO NOT include it** — leave a note: `[URL VERIFICATION NEEDED]`
5. If data cannot be sourced, **mark it clearly**: `[UNVERIFIED — needs manual check]`

### Priority 1: Link and Content Validation
- **Do not blindly trust a single provided link.** If a link is wrong, hallucinated, or contains contradictory info, the script will inherit those errors.
- **Cross-verify** claims with OTHER reputable sources before generating the script.
- If a provided link's content contradicts the *core premise* of the user's prompt (e.g., the link says "they won a trophy" but the prompt is strictly "without a trophy"), **prioritize the user's constraints** and find other valid sources that support the correct narrative, or omit the contradictory data completely.
- **Never expose contradictory spoiler text** in the reference URL slugs (e.g., using a URL with `/first-ipl-trophy/` for a video about never winning a trophy).


---

## Rule 1: Full URL References (MANDATORY)

Every generated script MUST include a `📚 References & Sources` section at the **end** of the file.

### Requirements:
- **FULL article URLs only** — never bare domains like `https://trak.in` or `https://www.space.com`
- Every data point, statistic, fact, or claim used in the script must be traceable to a source
- URLs must link to the **specific article/page/PDF** where the information was found
- Format as a markdown table with columns: `#`, `Data Point Used`, `Source`, `Link`

### Example (CORRECT ✅):
```
| 1 | Peak power demand 256.1 GW | Energy — Economic Times | https://energy.economictimes.indiatimes.com/news/power/indias-peak-power-demand-hits-record-256-gw/120621345 |
```

### Example (WRONG ❌):
```
| 1 | Peak power demand 256.1 GW | Economic Times | https://economictimes.indiatimes.com |
```

### Template:
```markdown
---

### 📚 References & Sources:

| # | Data Point Used | Source | Link |
|---|----------------|--------|------|
| 1 | [exact data point] | [publication name] | [FULL article URL] |
| 2 | ... | ... | ... |
```

---

## Rule 2: Pure DNA Adherence

- Every script must follow the creator's DNA profile exactly
- Include a DNA Adherence Audit section after the script body
- **Never name other YouTube creators or channels** in the script, audit, or hooks — describe forbidden traits only (e.g. "no bro slang", not "not GenZway")
- Voice comes only from the assigned creator's `CREATOR_MIND.md`, cheatsheet, `deep_hooks.md`, and transcripts

## Rule 2b: Transcript structure (MANDATORY — per topic)

> **Do not use one markdown table format for every creator.**

1. After `prepare.py`, read **REQUIRED FORMAT** at the bottom of `*_context.md` — it names a **matched reference video** (`data/<creator>/<video_id>/transcript.txt`).
2. **Copy that transcript's shape** — usually `[00:00]` inline lines, domino chains, or temple lists — not a generic 4-column table copied from another channel.
3. In DNA Audit, state: `Structure matched: <video_id> — <archetype key>`.
4. If topic is legal/civic (Niharika), geo/domino (Informed Citizen), or heritage list (Neha), pick the archetype `prepare.py` injected — do not override with Shivanshu/KK table format.

## Rule 2c: Dates in spoken script (anti wire-copy)

- **Research dates in browser** — they belong in the **references table** and in your notes.
- **Spoken script:** match the reference transcript's date density. For most ingested Niharika/Neha/Informed Citizen Shorts that is **zero dates in speech**.
- **Maximum:** one calendar date in the full script unless the reference uses more.
- **Forbidden pattern:** repeating `14 May 2026` / `15 May 2026` in multiple `[00:00]` lines (news ticker Hindi).
- Prefer: `is hafte`, `abhi`, `court ne order diya`, `kal ki hearing` — how creators actually talk.

Read **`CREATOR_SCRIPT_INTELLIGENCE.md`** before writing.

## Rule 2d: `*_dna.md` production file (mandatory sections)

Every finished script file must contain **only** these sections in order (no separate `*_BRIEF.md` / `*_context.md` required in repo):

1. **Title + Status** — creator name, post timing if known  
2. **`## HOOK PATTERN`** — table: pattern name, narrative arc, assignment hook (Hindi), adapted opener line  
3. **`## REFERENCE TRANSCRIPT`** — video ID, `data/<creator>/<id>/transcript.txt`, narrative pattern from `deep_hooks`  
4. **`### What we took from this transcript`** — table mapping reference device → this script line  
5. **`### Reference excerpt (verbatim)`** — 3–8 lines from ingested transcript (rhythm source, not facts)  
6. **`## FULL SCRIPT`** — `[00:00]` lines matching reference segment count ±1  
7. **`### DNA Adherence Audit`** — confirm hook + reference + phrase checklist  
8. **`## WATCH-THROUGH MAP`**  
9. **`## RESEARCHED RAW DATA`** — bullet points of all key factual data points, statistics, and figures gathered during live research  
10. **`### 📚 References & Sources`** — verified URLs only  

Agents must **read** `data/<creator>/<video_id>/transcript.txt` (or excerpt in prepare context) before writing — the DNA file must **name the video ID** and show the copy mapping.

## Rule 2e: Romanized Hinglish speech + hook rhythm (non-negotiable)

- **`## FULL SCRIPT` must be in Romanized Hindi (Latin letters)** — the on-camera style this repo uses: `Ek IPL season ki reach...`, `matlab`, `lekin`, `isliye`. Mix natural English for brands, stats, sports/business terms (JioStar, CTV, reach, playoff, broadcast).
- **Pure Devanagari walls are wrong** unless `*_context.md` **REQUIRED FORMAT** explicitly says Devanagari for that creator/topic (rare). Ingested transcripts may be Devanagari — still **write Romanized** for delivery; copy the **opener device**, not the script alphabet.
- **`[00:00]` hook line** must mirror the reference transcript's **first line shape** — same opener device, not a wire headline:
  - Reference: `फॉग ने इस तरह से...` → Script: `Fog ne is tarah se...` / `Adani group ne is tarah se...` (not a pasted English headline)
  - Reference: `यह घर चारों तरफ से...` → Script: `Yeh ghar charon taraf se...`
  - Reference: `मणिपुर में है पूरी दुनिया का सबसे बड़ा...` → Script: `Manipur mein hai poori duniya ka sabse bada...`
- **Segment count** = reference ±1 **or enough beats to hit Rule 2h** (whichever is larger).
- **Line length** = match reference density; for explainers use **long multi-clause lines** (25–45 words) where the reference does.
- **DNA audit** must quote: `Opening mimics: "<first 6–10 words of reference>" → "<first 6–10 words of script>"` (reference may be Devanagari; script line in Romanized).
- Wrong reference video (e.g. Ramnami story for Gangamma Jatra) = instant redo.

## Rule 2h: Minimum runtime — 2 minutes spoken (mandatory)

Shorts that die in 40–70s feel thin on camera. **Every `## FULL SCRIPT` must target ≥2 minutes (120s) wall-clock when read aloud** at the creator's pace.

| Check | Minimum |
|-------|---------|
| **Last timestamp** | `[01:55]` or later (prefer `[02:00]`–`[02:15]`) |
| **Word count** (FULL SCRIPT body only) | **≥360 words** @ ~3.0 WPS, or **≥320** @ ~2.7 WPS for slow creators (KKCreate, Neha) |
| **Beats** | **≥14** `[00:00]` lines for explainers; **≥12** only if reference is a proven sub-60s format and context allows |
| **Metadata** | Header must state: `Target runtime: ≥2:00 spoken \| ~360+ words (Romanized Hinglish)` |

**How to fill 2 minutes without fluff:** teach **one mechanism chain** with extra layers (context → how → twist → who pays → fan takeaway → CTA) — not repeated stats or date spam.

`python3 validate_script.py` enforces word count + last timestamp; fix failures before `PRODUCTION READY`.

## Rule 2f: Retention = teach one chain (not headline stack)

People stay for **unresolved questions**, not for a list of numbers. If the viewer can leave after line 1 knowing the whole story, the script failed.

### What the viewer must get (every script)

| After each beat | Viewer should think… |
|-----------------|----------------------|
| Hook | "Wait — that can't be right?" |
| Beat 2 | "Oh, *how* does that work?" |
| Middle | "So that's why…" (one link clearer) |
| Twist (`लेकिन`) | "I didn't expect that" |
| Close (`इसीलिए` / CTA) | "Now I get what it means for me" |

### WATCH-THROUGH MAP (required column)

```markdown
| Phase | Time | Viewer question (why they stay) | Beat |
```

Every row needs a **question the viewer still needs answered** until CLOSE.

### Mechanism vs headline stack (anti-hallucination)

| FAIL (do not write) | PASS (imitate reference) |
|---------------------|--------------------------|
| `₹500 करोड़ नुकसान, pool ₹1.98 लाख करोड़, ICRA hike` | `जब क्रूड ऊपर और पंप कीमत पीछे → हर लीटर घाटा → ₹3 के बाद भी ₹500 करोड़/दिन` |
| Hook = assignment `hook_hindi` pasted as wire copy | Hook = **reference first-line shape** in **Romanized Hinglish** |
| Reference = wrong video (mapping table lies) | Reference teaches **same narrative job** (how / list / legal / geo) |
| 4 stats, zero taught links | Each `[00:00]` answers the **previous** open question |

**Shivanshu mechanism references** (e.g. `y7qQ3N40Flc` LPG): after `फैक्ट्स सरप्राइज़`, start **`जब…`** in the **same breath** — teach pump → refinery → cap → loss, not agency names.

**Gold example (OMC topic, shape from `y7qQ3N40Flc`):**  
`पेट्रोल महंगा हुआ, फिर भी… फैक्ट्स सरप्राइज़ कर देंगे — जब आप पंप पर ₹3 देखते हैं तो लगता है फायदा, लेकिन…`

### DNA Adherence Audit (required lines)

```markdown
- Opening mimics: "<reference first 6–10 words>" → "<script first 6–10 words>"
- Teaches [one chain / list / legal meaning] — not headline stack ✅
- Viewer questions mapped in WATCH-THROUGH MAP ✅
```

## Rule 2g: Pre-flight checklist (agent — before PRODUCTION READY)

- [ ] Read **full** `data/<creator>/<ref_id>/transcript.txt` (not excerpt only)
- [ ] Reference video matches **narrative job** (mechanism / list / digest / geo)
- [ ] `[00:00]` = reference opener shape + **Romanized Hinglish** (not pure Devanagari wall)
- [ ] **≥2:00 spoken** — last stamp ≥`[01:55]`, ≥360 words (or ≥320 slow WPS)
- [ ] Segment count ±1 vs reference **or** enough beats for 2 min; line length similar / dense
- [ ] `WATCH-THROUGH MAP` has **Viewer question** column filled
- [ ] Facts only from verified URLs in references table
- [ ] `python3 validate_script.py ...` passes (fix warnings that are errors in disguise)

## Rule 2i: Creator-Specific Transitions (Anti-Listing)

- **Do NOT use generic enumerators** like "Pehla reason hai...", "Dusra point yeh hai...", "Teesra factor...". This sounds like a generic AI or textbook, not a creator.
- **Instead, use the creator's actual transition mechanics.** Look at the reference transcript. Use their specific logical pivots (e.g., "Jab aap X dekhte hain, toh lagta hai Y... Lekin asali game Z mein hai", or "Iske peeche sabse bada khel yeh hai ki... Aur isse bhi badi baat...").
- Structural flow must be cause-and-effect driven, maintaining narrative momentum, rather than just reading out bullet points.

## Rule 3: Anti-Repetition

- Rotate hook types across scripts for the same creator
- Rotate closing types across scripts for the same creator
- Never use the same structure twice in a row
