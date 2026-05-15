"""Per-creator script output formats — agents must follow exactly."""

from __future__ import annotations

import re

VOICE_MARKERS: dict[str, dict[str, list[str]]] = {
    "Shivanshu.Agrawal": {
        "required_any": ["lekin", "isliye"],
        "required_one_of": ["actually", "ultimately", "kya aapko pata hai"],
        "cta_any": [
            "aisi aur video ke liye channel ko subscribe",
            "aise explainer videos ke liye mujhe follow",
        ],
        "forbidden": ["bhai", "tum log", "naatak", "gandi tarah"],
    },
    "KKCreate": {
        "required_any": ["par ", "yahan tak ki"],
        "required_one_of": ["ke according", "reports ke according"],
        "cta_any": ["mausam badalta rehta hai"],
        "forbidden": ["bhai", "subscribe karein", "follow zaroor"],
    },
    "NehaGupta": {
        "required_any": ["hamari sanskriti", "garv", "darshan"],
        "required_one_of": ["devbhoomi", "chamatkari", "mahima", "kya aap jaante hain"],
        "cta_any": ["comment mein"],
        "forbidden": ["bhai", "naatak", "subscribe karein"],
    },
    "PrabhjotSpeaks": {
        "required_any": ["lekin kya", "asli sawal"],
        "required_one_of": ["reports ke according", "yahi poori picture"],
        "cta_exact": [
            "aise aur current affairs ke liye mujhe follow zaroor karna"
        ],
        "forbidden": ["bhai", "gandi tarah"],
    },
    "ThinkSchool_Hindi": {
        "required_any": ["lekin"],
        "required_one_of": ["business", "lesson", "matlab", "entrepreneur"],
        "cta_any": ["follow karo", "follow karein"],
        "forbidden": ["bhai", "naatak"],
    },
    "NiharikaChoudhary": {
        "required_any": ["simple", "matlab", "aapko"],
        "required_one_of": ["samjho", "yaad rakhna", "explained"],
        "cta_any": ["follow karo", "comment"],
        "forbidden": ["bhai", "gandi tarah"],
    },
    "TheInformedCitizen": {
        "required_any": ["seedha matlab", "doston", "दोस्तों"],
        "required_one_of": ["matlab", "background", "lekin"],
        "cta_any": ["subscribe", "follow", "comment", "share karo", "बताएं"],
        "forbidden": ["bhai", "naatak"],
    },
}


OUTPUT_FORMAT: dict[str, str] = {
    "Shivanshu.Agrawal": """
## REQUIRED FORMAT: Shivanshu.Agrawal
- **Table:** `| Timestamp | Hindi Script | Pacing (WPS) | Context/Visuals |` — **7–9 rows**, ~55–70s
- **WPS:** 3.0–3.4 measured documentary pace
- **Voice:** Third-person narrator. Formal Hindi. NO "bhai", NO outrage.
- **Must include:** `Actually`, `Lekin`, `Isliye`, `Ultimately` (each once in body)
- **CTA (exact):** `Aisi aur video ke liye channel ko subscribe karein.`
- **Hook:** Declarative fact or `Kya aapko pata hai` — never "Aaj hum baat karenge"
""",
    "KKCreate": """
## REQUIRED FORMAT: KKCreate
- **Table:** `| Timestamp | Hindi Script | Pacing (WPS) | Context/Visuals |` — **7–8 rows**, ~55–65s
- **WPS:** 2.4–2.5 slow ground-reporting
- **Open:** Place/nostalgia scene — then dated shock fact
- **Must include:** `Par` pivot, `Yahan tak ki` escalation, **vox-pop** (quoted local voice)
- **Close (exact style):** `Mausam badalta rehta hai, lekin jab wo apna mizaaj badal le, toh samajh lena chahiye ki khatra nazdeek hai.`
- **NO subscribe CTA**
""",
    "NehaGupta": """
## REQUIRED FORMAT: NehaGupta (default — overridden per topic in context)
- **Primary shape:** real ingested `[00:00]` timestamp lines (temple list, `Kya aap jaante hain`, regional discovery) — see matched reference in `*_context.md`
- **NOT:** Shivanshu/KK 4-column table, Niharika legal table, or generic news anchor
- **Must include:** `darshan`, `hamari sanskriti` or `garv`, `Comment mein [X]` CTA
- Director/fenced blocks only if the **reference transcript** for that topic uses them
""",
    "PrabhjotSpeaks": """
## REQUIRED FORMAT: PrabhjotSpeaks
- **Table:** `| Timestamp | Script | Pattern Stage |` — **6–7 rows**
- **Open:** `[Event]. Lekin kya [assumption]?`
- **Must include:** `Asli sawal yeh hai`, `Reports ke according`, timing pivot, open question
- **CTA (exact, last line):** `Aise aur current affairs ke liye mujhe follow zaroor karna.`
""",
    "ThinkSchool_Hindi": """
## REQUIRED FORMAT: ThinkSchool_Hindi
- **Table:** `| Timestamp | Hindi Script | Pattern Stage |` — **6–8 rows**
- Shock stat open + numbered beats + `Lekin` business lesson
- **Close:** Entrepreneur takeaway + follow CTA from cheatsheet
""",
    "NiharikaChoudhary": """
## REQUIRED FORMAT: NiharikaChoudhary (default — overridden per topic in context)
- **Primary shape:** `[00:00]` timestamp prose like ingested transcripts — `Aakhir kya hua`, `Aap khud sochiye`, civic/legal clarity
- **Avoid** generic markdown `| Timestamp | Script | Pattern |` unless the matched reference video uses it (most don't)
- **CTA:** `Aap kya sochte hain?` + comment / follow journalist
""",
    "TheInformedCitizen": """
## REQUIRED FORMAT: TheInformedCitizen (default — overridden per topic in context)
- **Geo Shorts:** open `दोस्तों, [region] की geography...` — match reference in context (NOT wire-news dates)
- **Citizen impact:** `Seedha matlab aapke liye`, `Background mein samajhna zaroori hai` — from CREATOR_MIND
- **Do NOT** force `Dar-asal` / `Aaiye samajhte hain` unless the matched reference transcript uses them
- Flowing `[00:00]` prose + map cues; never Shivanshu 4-column table
""",
}


def get_output_format(creator: str) -> str:
    return OUTPUT_FORMAT.get(
        creator,
        "- Use timestamp table, 6+ rows, creator CTA from context cheatsheet.",
    )


def check_voice_markers(markdown: str, creator: str) -> list[str]:
    """Return list of voice violations (empty = OK)."""
    spec = VOICE_MARKERS.get(creator)
    if not spec:
        return []
    low = markdown.lower()
    errors: list[str] = []

    for phrase in spec.get("forbidden", []):
        if re.search(r"\b" + re.escape(phrase) + r"\b", low):
            errors.append(f"Forbidden voice phrase: '{phrase}'")

    for phrase in spec.get("required_any", []):
        if phrase not in low:
            errors.append(f"Missing required voice marker (need one of group): '{phrase}'")

    one_of = spec.get("required_one_of", [])
    if one_of and not any(p in low for p in one_of):
        errors.append(f"Missing signature phrase — need one of: {one_of}")

    cta_exact = spec.get("cta_exact", [])
    if cta_exact and not any(c in low for c in cta_exact):
        errors.append(f"Missing exact CTA: {cta_exact[0]}")

    cta_any = spec.get("cta_any", [])
    if cta_any and not any(c in low for c in cta_any):
        errors.append(f"Missing CTA pattern — need one of: {cta_any}")

    return errors
