import json
import subprocess

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
        print(f"Generating for {mapped_name}: {t_title}")
        subprocess.run(['python3', 'prepare.py', '-c', mapped_name, '-t', t_title])
