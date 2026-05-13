#!/bin/bash
# Slow ingestion script — fetches transcripts one at a time with 30s delays
# Designed to work around YouTube 429 rate limits

CREATOR="KKCreate"
LIMIT=50
DELAY=30  # seconds between each video

echo "🐢 Slow Ingestion Mode: $DELAY second delay between videos"
echo "⏳ Initial cooldown: 15 minutes..."
sleep 900

echo "🚀 Starting slow ingestion for $CREATOR (limit: $LIMIT)..."
python3 ingest.py --creator "$CREATOR" --limit "$LIMIT" --marathon --verbose 2>&1
