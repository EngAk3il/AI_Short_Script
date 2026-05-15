# Script Generation Rules 📋

> These rules MUST be followed for EVERY script generated in this system.
> Last updated: 2026-05-12

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

## Rule 3: Anti-Repetition

- Rotate hook types across scripts for the same creator
- Rotate closing types across scripts for the same creator
- Never use the same structure twice in a row
