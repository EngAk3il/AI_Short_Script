import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.chrome_fallback import fetch_transcript_via_chrome

logging.basicConfig(level=logging.INFO)

def test(video_id):
    print(f"Testing Chrome extraction for: {video_id}")
    try:
        segments, lang = fetch_transcript_via_chrome(video_id)
        print(f"✅ Success! Found {len(segments)} segments in lang: {lang}")
        for s in segments[:3]:
            print(f"  [{s['start']}] {s['text']}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    # Test with the Ethan Shaw video that hung
    test("cLKUrXPuPk8")
