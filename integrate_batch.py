import json
import os
from datetime import datetime, timezone

def integrate_transcript(data_dir, creator_name, video_data):
    video_id = video_data['video_id']
    language = video_data.get('language', 'hi') # Default to hi if not specified
    if language.lower() == 'hindi': language = 'hi'
    if language.lower() == 'english': language = 'en'
    
    segments = []
    for entry in video_data['transcript']:
        # Convert "M:SS" to float seconds
        parts = entry['start'].split(':')
        start_secs = 0.0
        if len(parts) == 2:
            start_secs = float(int(parts[0]) * 60 + int(parts[1]))
        elif len(parts) == 3:
            start_secs = float(int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2]))
        
        segments.append({
            'start': start_secs,
            'duration': 0.0, # Will compute later
            'text': entry['text']
        })
    
    # Compute durations
    for i in range(len(segments) - 1):
        segments[i]['duration'] = segments[i+1]['start'] - segments[i]['start']
    if segments:
        segments[-1]['duration'] = 3.0 # Default
        
    video_dir = os.path.join(data_dir, creator_name, video_id)
    os.makedirs(video_dir, exist_ok=True)
    
    # Write transcript.json
    with open(os.path.join(video_dir, 'transcript.json'), 'w', encoding='utf-8') as f:
        json.dump({
            'video_id': video_id,
            'language': language,
            'source': 'antigravity-browser',
            'segments': segments
        }, f, indent=2, ensure_ascii=False)
    
    # Write transcript.txt
    with open(os.path.join(video_dir, 'transcript.txt'), 'w', encoding='utf-8') as f:
        for seg in segments:
            m = int(seg['start'] // 60)
            s = int(seg['start'] % 60)
            f.write(f"[{m:02d}:{s:02d}] {seg['text']}\n")
            
    # Update metadata.json (read existing if available)
    meta_path = os.path.join(video_dir, 'metadata.json')
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    
    meta.update({
        'video_id': video_id,
        'channel': creator_name,
        'transcript_status': 'OK',
        'transcript_language': language,
        'transcript_source': 'antigravity-browser',
        'segment_count': len(segments),
        'ingested_at': datetime.now(timezone.utc).isoformat()
    })
    
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    
    # Update _channel_meta.json
    channel_meta_path = os.path.join(data_dir, creator_name, '_channel_meta.json')
    if os.path.exists(channel_meta_path):
        with open(channel_meta_path, 'r', encoding='utf-8') as f:
            channel_meta = json.load(f)
        
        # Update the specific video status
        updated = False
        for v in channel_meta.get('videos', []):
            if v['video_id'] == video_id:
                v['status'] = 'OK'
                updated = True
                break
        
        if updated:
            # Recompute stats
            stats = channel_meta.get('ingestion_stats', {})
            # This is a bit complex since we don't know the previous status easily from here
            # But we can just recount everything
            ok_count = sum(1 for v in channel_meta['videos'] if v.get('status') == 'OK')
            stats['ok'] = ok_count
            channel_meta['ingestion_stats'] = stats
            
            with open(channel_meta_path, 'w', encoding='utf-8') as f:
                json.dump(channel_meta, f, indent=2, ensure_ascii=False)
    
    print(f"Integrated {video_id} for {creator_name}")

if __name__ == "__main__":
    import sys
    # Expecting JSON data from stdin
    data = json.load(sys.stdin)
    data_dir = "data"
    for v in data:
        creator = v.get('creator', 'TheInformedCitizen')
        current_data_dir = "strategy_data" if v.get('type') == 'strategy' else data_dir
        integrate_transcript(current_data_dir, creator, v)
