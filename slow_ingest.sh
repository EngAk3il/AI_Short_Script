#!/bin/bash
# Reliable slow ingest — cookies + retry-friendly delays
set -euo pipefail
cd "$(dirname "$0")"

CREATOR="${1:-KKCreate}"
LIMIT="${2:-50}"
COOKIES="${COOKIES:-cookies.txt}"

if [[ ! -f "$COOKIES" ]]; then
  echo "⚠️  No $COOKIES — export from Chrome:"
  echo "   yt-dlp --cookies-from-browser chrome --cookies cookies.txt --skip-download 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'"
  exit 1
fi

echo "🐢 Slow ingest: $CREATOR (limit $LIMIT) with $COOKIES"
python3 ingest.py \
  --creator "$CREATOR" \
  --limit "$LIMIT" \
  --cookies "$COOKIES" \
  --delay 18 \
  --pause-every 10 \
  --pause-seconds 120 \
  --retry-failed \
  "$@"
