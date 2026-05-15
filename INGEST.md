# Transcript ingestion — avoid IP blocks

YouTube blocks bulk transcript fetching after ~20–50 requests from the same IP. **Selenium is slow and breaks often.** The reliable fix is **browser cookies + smart pacing**.

---

## Best setup (recommended)

### 1. Export cookies once

**Option A — yt-dlp from Chrome (easiest on Mac):**
```bash
# Log into YouTube in Chrome first, then:
yt-dlp --cookies-from-browser chrome --cookies cookies.txt --skip-download "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```
This creates `cookies.txt` in the project root.

**Option B — browser extension:**  
Export Netscape-format `cookies.txt` (e.g. "Get cookies.txt LOCALLY") while logged into YouTube.

Place file at: `AI_Short_Script/cookies.txt` (add to `.gitignore` — never commit).

### 2. Ingest with cookies + sane delays

```bash
python3 ingest.py -c Shivanshu.Agrawal --cookies cookies.txt --delay 12
```

### 3. If you get blocked mid-run

The tool marks videos as `RATE_LIMITED` (not permanent failure). Resume later:

```bash
# Wait 30–60 min OR switch network, then:
python3 ingest.py -c Shivanshu.Agrawal --retry-failed --cookies cookies.txt --delay 20 --marathon
```

Check status:
```bash
python3 ingest_status.py -c Shivanshu.Agrawal
python3 ingest_status.py -c Shivanshu.Agrawal --export-retry-urls
```

---

## Commands

| Command | Purpose |
|---------|---------|
| `ingest.py -c NAME` | New videos only (skips OK transcripts) |
| `ingest.py -c NAME --retry-failed` | Retry blocked/failed only |
| `ingest.py -c NAME --cookies cookies.txt` | Use logged-in session |
| `ingest.py -c NAME --cookies-from-browser chrome` | Read cookies directly from Chrome |
| `ingest.py -c NAME --delay 15` | 15s between videos |
| `ingest.py -c NAME --marathon` | Extra slow (25s delay, 3min pause every 8 videos) |
| `ingest.py -c NAME --pause-every 10 --pause-seconds 180` | Custom cooldown batching |
| `ingest.py -c NAME --proxy http://127.0.0.1:8080` | Optional proxy |

Environment variables:
```bash
export YT_COOKIES_FILE=/path/to/cookies.txt
export YT_COOKIES_BROWSER=chrome
export YT_DELAY=12
export YT_PROXY=http://127.0.0.1:8080
```

---

## Fluent workflow for ALL transcripts

```bash
# 1. Status
python3 ingest_status.py -c GenZway

# 2. First pass (with cookies)
python3 ingest.py -c GenZway --cookies cookies.txt --delay 10 --pause-every 12 --pause-seconds 90

# 3. Retry anything blocked
python3 ingest.py -c GenZway --retry-failed --cookies cookies.txt --delay 15

# 4. Learn patterns (one entry per transcript video_id)
python3 deep_hook_status.py
python3 deep_hook_learn.py GenZway          # missing transcripts only
python3 deep_hook_learn.py --all GenZway    # full rebuild
```

For **many creators**, run one creator at a time — not marathon across 10 channels in one session.

---

## Browser fallback (Antigravity — no IP block on API)

When API ingest keeps failing, capture captions in the browser and import:

1. Open Short on YouTube → show transcript panel → copy or extract segments
2. Pipe JSON to `integrate_batch.py` (see existing `antigravity-browser` flow in `data/`)

This is slower but **never hits transcript API rate limits**.

---

## Why Selenium fails

- YouTube detects automation → captcha / block
- Heavy and unstable for hundreds of Shorts
- Cookies + yt-dlp is faster and what most archivers use

Use Selenium only as last resort; prefer **cookies.txt + ingest.py --retry-failed**.
