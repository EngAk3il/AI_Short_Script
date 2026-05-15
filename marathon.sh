#!/bin/bash

# List of creators in priority order
PRIORITY_CREATORS=("TheInformedCitizen" "NiharikaChoudhary" "NehaGupta" "UditInsights" "TubeBuddy")
OTHER_CREATORS=("Nitishrajputshorts" "GenZway" "Shivanshu.Agrawal" "hellooipsita" "Finsaheliofficial" "ThinkSchool_Hindi" "AshutoshPratihastAP" "PrabhjotSpeaks" "MattGray" "AlexHormozi" "EthanShaw" "KKCreate" "MangeshShinde" "openletteryt")

LIMIT=50
DELAY=20

echo "Starting Marathon Ingestion..."

# First pass: Priority Creators
for creator in "${PRIORITY_CREATORS[@]}"; do
    echo "Processing Priority Creator: $creator"
    python3 ingest.py --creator "$creator" --limit $LIMIT --marathon
    sleep 5
done

# Second pass: Other Creators
for creator in "${OTHER_CREATORS[@]}"; do
    echo "Processing Creator: $creator"
    python3 ingest.py --creator "$creator" --limit $LIMIT --marathon
    sleep 5
done

echo "Marathon Ingestion Complete."
