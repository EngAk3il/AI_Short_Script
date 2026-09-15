import json
import subprocess
import os
from glob import glob

mapping = {
    "Shivanshu Agrawal": "Shivanshu.Agrawal",
    "KK Create": "KKCreate",
    "Think School": "ThinkSchool_Hindi",
    "Sports Edge (Cricket Facts)": "SportsEdge",
    "Prabhjot Speaks": "PrabhjotSpeaks",
    "Niharika Choudhary": "NiharikaChoudhary",
    "The Informed Citizen": "TheInformedCitizen",
    "Neha Gupta": "NehaGupta",
    "Professor of How": "ProfessorOfHow"
}

with open('final_topics.json') as f:
    data = json.load(f)

for creator in data['creators']:
    c_name = creator['creator_category']
    mapped_name = mapping.get(c_name, c_name)
    for topic in creator['topics']:
        t_title = topic['title_data']['title']
        print(f"Auto-generating for {mapped_name}: {t_title}")
        subprocess.run(['python3', 'generate.py', '--auto', '-c', mapped_name, '-t', t_title])

# Now remove unwanted files
print("Cleaning up unwanted .md files...")
for file_path in glob('scripts/**/*_BRIEF.md', recursive=True):
    os.remove(file_path)
    
for file_path in glob('scripts/**/*_context.md', recursive=True):
    os.remove(file_path)

print("All done!")
