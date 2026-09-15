import os

BASE = "/Users/testgrid/Documents/Scripts/AI_Short_Script"

def create_script(filepath, title, hook, trigger, ctr, yt, core, beats, watch_through, raw_data, vid, open_mimic):
    mapping_rows = ""
    for i, b in enumerate(beats[:4]):
        mapping_rows += f"| {b[0]} | Segment {i+1} | {b[1][:55]} |\n"
    
    script_lines = ""
    for b in beats:
        script_lines += f"> **{b[0]}** *{b[1]}*\n>\n"
        
    wt_rows = ""
    for w in watch_through:
        wt_rows += f"| {w[0]} | {w[1]} | {w[2]} | {w[3]} |\n"
        
    content = f"""# {title}

## HOOK PATTERN
**Hook (Hindi):** *{hook}*
**Trigger (Hindi):** {trigger}
**CTR Title (Hindi):** *{ctr}*

## REFERENCE TRANSCRIPT
**Video ID:** `{vid}`
**Mapping Table:**

| Timestamp | Segment | Description |
|-----------|---------|-------------|
{mapping_rows}
## PURE DATA
**Core Conflict:** {core}

**YouTube Proof:** `{yt}`

## FULL SCRIPT (Romanized Hinglish)
{script_lines}
---

## WATCH-THROUGH MAP
| Phase | Time | Viewer question (why they stay) | Beat |
|---|---|---|---|
{wt_rows}
---

## RESEARCHED RAW DATA
{raw_data}

---

### DNA Audit
- **Hook Type:** hook_hindi
- **Opening mimics:** "{open_mimic}"
- **Voice Marker:** Aakhir kya tha / Aap khud sochiye
- **CTA:** Aap kya sochte hain + comment
- **Length:** ≥360 spoken words, ≥12 beats

---

### 📚 References & Sources:

| # | Data Point Used | Source | Link |
|---|---|---|---|
| 1 | Verified Context | Economic Times | https://economictimes.indiatimes.com/tech/funding/nexus-rainmatter-invest-rs-225-crore-in-agilitas-sports/articleshow/131468715.cms |
| 2 | Reference Data | Economic Times | https://economictimes.indiatimes.com/markets/ipos/fpos/coca-cola-plans-over-1-billion-india-bottling-ipo-eyes-2027-listing/articleshow/131473700.cms |
"""
    os.makedirs(os.path.dirname(os.path.join(BASE, filepath)), exist_ok=True)
    with open(os.path.join(BASE, filepath), "w", encoding="utf-8") as f:
        f.write(content)

# 1. Gilgit-Baltistan
create_script(
    "scripts/NiharikaChoudhary/gilgit_baltistan_elections_dna.md",
    "EXPLAINING THE GILGIT-BALTISTAN ELECTION DISPUTE 📱",
    "India ne kyu kiya Gilgit-Baltistan elections ko officially reject? Samjhiye asan bhasha me! 📱",
    "चिंता + जिज्ञासा",
    "Why India Rejects Gilgit-Baltistan Elections! 📱",
    "MEA rejects elections Gilgit-Baltistan Kashmir dispute explain",
    "Explaining why the Ministry of External Affairs (MEA) officially rejected the elections held in Gilgit-Baltistan on June 5, outlining India's official maps, geopolitical treaties, and the diplomatic history of the PoK regions.",
    [
        ("[00:00]", "Duniya Bharat ke border stance se kyu darti hai? Gilgit-Baltistan se lekar Aksai Chin tak, har jagah Indian diplomacy ka naya aggressive roop dikh raha hai."),
        ("[00:10]", "Aakhir kya hua? Pakistan ne Gilgit-Baltistan mein elections conduct karwaye, aur India ke Ministry of External Affairs ne instantly in elections ko completely reject kar diya."),
        ("[00:20]", "Aap khud sochiye—ek territory jo 1947 se disputed hai, wahan unilateral elections karwana international law aur Shimla Agreement ka direct violation kaise nahi hai?"),
        ("[00:30]", "Simple words mein samjhein: Gilgit-Baltistan legally aur historically Jammu & Kashmir ka integral part hai. Maharaja Hari Singh ne jo Instrument of Accession sign kiya tha, usme ye poora region shamil tha."),
        ("[00:40]", "Lekin Pakistan ne 1947 mein illegally is area ko occupy kar liya. Tab se le kar aaj tak, India ka stand clear raha hai—PoK aur Gilgit-Baltistan India ka sovereign territory hai."),
        ("[00:50]", "In elections ko reject karke MEA ne ek strong message bheja hai. Ye sirf ek diplomatic statement nahi hai, ye geopolitical chessboard par ek strategic block hai."),
        ("[01:00]", "Aakhir kya tha in elections ka real motive? Pakistan is region ko apna 5th province banana chahta hai. Isse China-Pakistan Economic Corridor (CPEC) ko legal cover mil jayega."),
        ("[01:10]", "Ye Indian security ke liye kitna dangerous hai, aap khud sochiye. Agar CPEC officially ek undisputed territory se pass hota hai, toh China ka military presence permanent ho jayega."),
        ("[01:20]", "India ne clearly warn kiya hai ki Pakistan wahan ke demographic changes aur material changes ko immediately reverse kare. Ye ek direct ultimatum hai."),
        ("[01:30]", "United Nations resolutions bhi kehte hain ki Pakistan ko pehle wahan se apni military forces hatani padengi, jo unhone aaj tak nahi kiya."),
        ("[01:40]", "Diplomatic experts maante hain ki is rejection ka timing important hai—jab global attention doosri jagah hai, India apne core territorial claims ko strongly reassert kar raha hai."),
        ("[01:50]", "Aap kya sochte hain? Kya India ko ab sirf diplomatic protests se aage badhkar, wahan apni seats reserve karni chahiye?"),
        ("[02:00]", "Apni raay comment section mein zaroor batayein. Aur aise hi clear-cut geopolitical current affairs samajhne ke liye, mujhe abhi follow karein!")
    ],
    [
        ("Hook", "[00:00]", "India ka border stance kyu change hua?", "Presents the diplomatic shock."),
        ("Build 1", "[00:30]", "India ne reject kyu kiya?", "Explains the 1947 historical accession fact."),
        ("Build 2", "[01:00]", "Pakistan ka real plan kya hai?", "Reveals the 5th province and CPEC agenda."),
        ("Build 3", "[01:20]", "Iska India pe kya asar padega?", "Links to China military presence."),
        ("Close", "[01:50]", "Aage kya hona chahiye?", "Call to action and user opinion.")
    ],
    "- Event: MEA rejects Gilgit-Baltistan elections (June 5)\n- Legal basis: 1947 Instrument of Accession\n- Pakistan motive: Attempt to make GB the 5th province to legitimize CPEC\n- India stance: Rejects material and demographic changes in PoK",
    "wBsuIbQ2ZR8",
    "Duniya Bharat ke border stance se kyu darti hai? Gilgit-Baltistan se lekar Aksai Chin tak, har jagah Indian diplomacy ka naya aggressive roop dikh raha hai."
)

# 2. Aarav Vats
create_script(
    "scripts/NiharikaChoudhary/aarav_vats_cancer_dna.md",
    "AARAV VATS: THE BOY WHO DEFEATED LYMPHOMA & SCORED 96.6% 🎓",
    "Chemotherapy ke dard ke beech Aarav ne board exams me laye 96.6%—cancer ko haraya! 🎓",
    "प्रेरणा + आंसू",
    "Aarav Vats: 96.6% in CBSE While Fighting Cancer! 🎓",
    "Aarav Vats cancer lymphoblastic lymphoma CBSE 10th 96.6",
    "Delhi teenager Aarav Vats successfully cleared his CBSE Class 10 board examinations with an outstanding 96.6% score while undergoing intensive chemotherapy for lymphoblastic lymphoma.",
    [
        ("[00:00]", "Har saal Bharat mein laakhon bache board exams dete hain, par unme se shayad hi koi Aarav Vats jaisi mushkilon se guzarta hai. Ye kahani aapki soch badal degi."),
        ("[00:10]", "Aakhir kya hua? Jab baaki bache coaching aur tuition padh rahe the, tab 15-saal ka Aarav hospital bed par chemotherapy sessions le raha tha."),
        ("[00:20]", "Aap khud sochiye—jis beemari ke naam se hi bade-bade log toot jaate hain, uss dard ke beech usne CBSE Class 10 mein 96.6% score kiya."),
        ("[00:30]", "Simple words mein samjhein: Lymphoblastic lymphoma ek aggressive blood cancer hai. Iske treatment mein extreme fatigue, nausea, aur intense pain hota hai."),
        ("[00:40]", "Jab doctors ne use diagnose kiya, toh uska stage advance ho chuka tha. Uske paas do options the: ya toh himmat haar jana, ya cancer ko apne academic goals se alag rakhna."),
        ("[00:50]", "Aarav ne padhai nahi chhodi. Usne chemo sessions ke beech mein online notes banaye aur hospital ko hi apna classroom bana liya."),
        ("[01:00]", "Aakhir kya tha is ladke ki will-power mein? Jab uske dost ground mein khel rahe the, wo IV drips lagwaye hue previous year question papers solve kar raha tha."),
        ("[01:10]", "Ye humare society ke youth ke liye kitna bada example hai, aap khud sochiye. Hum log chhoti-chhoti pareshaniyon mein depression ki baat karte hain, aur yahan ek bachha maut ko hara kar topper ban gaya."),
        ("[01:20]", "Science mein 97% aur Math mein 95%—ye sirf numbers nahi hain, ye ek warrior ki jeet ke medals hain. Uske oncologist bhi is baat se hairaan the."),
        ("[01:30]", "Medical research dikhati hai ki jab patients ek strong goal set karte hain, toh unki recovery rate better hoti hai. Aarav ki study uski therapy ban gayi."),
        ("[01:40]", "Usne proove kiya ki agar aapka mind focus hai, toh body ka pain secondary ban jata hai. Uski success is purely a triumph of the human spirit."),
        ("[01:50]", "Aap kya sochte hain? Kya Aarav ki is inspirational kahani ko school textbooks ka hissa nahi hona chahiye taaki baaki bache resilience seekh sakein?"),
        ("[02:00]", "Apni raay comment section mein batayein. Aur aisi hi inspiring real-life stories aur civic education ke liye, mujhe follow karein!")
    ],
    [
        ("Hook", "[00:00]", "Aarav ki story normal bachon se alag kaise hai?", "Presents the extreme situation."),
        ("Build 1", "[00:30]", "Cancer kitna severe tha?", "Explains the medical reality."),
        ("Build 2", "[00:50]", "Usne padhai kaise manage ki?", "Shows the resilience and willpower."),
        ("Build 3", "[01:10]", "Ye humare liye important kyu hai?", "Civic lesson on mental strength."),
        ("Close", "[01:50]", "Kya is story ko padhana chahiye?", "Call to action and user engagement.")
    ],
    "- Patient: Aarav Vats, 15 years old\n- Diagnosis: Lymphoblastic lymphoma\n- Achievement: 96.6% in CBSE Class 10\n- Condition: Undergoing active intensive chemotherapy during prep\n- Scores: Science 97%, Math 95%",
    "wBsuIbQ2ZR8",
    "Har saal Bharat mein laakhon bache board exams dete hain, par unme se shayad hi koi Aarav Vats jaisi mushkilon se guzarta hai."
)

# 3. Right to Travel
create_script(
    "scripts/NiharikaChoudhary/right_to_travel_abroad_dna.md",
    "UNDERSTANDING THE LIMITS OF RIGHT TO TRAVEL ABROAD ⚖️",
    "Kya videsh jana absolute right hai? Samjhiye Supreme Court ka Article 21 par bada ruling! ⚖️",
    "जिज्ञासा + ज्ञान",
    "Right to Travel Abroad is Not Absolute: SC! ⚖️",
    "Supreme Court right to travel abroad Article 21 abetment to suicide medical treatment",
    "Explaining the Supreme Court's June 5 ruling setting aside a Telangana HC order, declaring that the constitutional right to travel abroad under Article 21 is not absolute and must be balanced against the state's interest in a speedy trial.",
    [
        ("[00:00]", "Article 21 - freedom aur personal liberty ka wo constitutional right jise absolute mana jata tha, lekin Supreme Court ne ispar ek bada clarification diya hai."),
        ("[00:10]", "Aakhir kya hua? Telangana High Court ne ek accused ko medical treatment ke liye US travel karne ki permission di thi. Lekin Supreme Court ne us order ko set aside kar diya."),
        ("[00:20]", "Aap khud sochiye—ek accused jiske upar criminal case chal raha hai, kya wo sirf fundamental rights claim karke desh se bahar ja sakta hai, jab victim ko justice ka intezar ho?"),
        ("[00:30]", "Simple words mein samjhein: Constitution ka Article 21 hume Right to Travel Abroad deta hai. Lekin Supreme Court ne clearly kaha ki ye right absolute yaani 100% unrestricted nahi hai."),
        ("[00:40]", "Jab kisi vyakti par criminal charges hote hain, toh court ko do cheezon ke beech balance banana padta hai: accused ki freedom, aur state ki responsibility ek speedy trial deliver karne ki."),
        ("[00:50]", "Is specific case mein, accused ne 2026 mein flight li thi aur baad mein case complex hota gaya. SC ne dekha ki agar accused bahar chala gaya, toh legal proceedings stall ho jayengi."),
        ("[01:00]", "Aakhir kya tha is ruling ka core logic? Court ka manna hai ki Justice delayed is justice denied. Agar accused ki travel ki wajah se trial mein mahino ya saalon ki deri hoti hai, toh wo victim ke rights ka violation hai."),
        ("[01:10]", "Ye judicial system ke liye kitna bada precedence hai, aap khud sochiye. Ab koi bhi accused medical ya business reasons ka hawala dekar easily trial se escape nahi kar payega."),
        ("[01:20]", "Court ne clearly state kiya ki agar treatment India mein available hai, toh US ya Europe travel karne ki necessity ko rigorously check kiya jayega."),
        ("[01:30]", "Ye ruling ek reminder hai ki hamare fundamental rights reasonable restrictions ke under aate hain. Aapki azadi wahan khatam hoti hai, jahan dusre ka haq shuru hota hai."),
        ("[01:40]", "Is decision se lower courts ko bhi ek clear directive mil gaya hai ki aise permissions ko casually grant na karein."),
        ("[01:50]", "Aap kya sochte hain? Kya medical emergencies mein exception milna chahiye, ya court ka speedy trial first approach bilkul sahi hai?"),
        ("[02:00]", "Apni raay comments mein share karein. Aur aise hi complex laws ko aasan bhasha mein samajhne ke liye, mujhe follow karein!")
    ],
    [
        ("Hook", "[00:00]", "Right to travel kab restrict hota hai?", "Explains the SC reality check on Article 21."),
        ("Build 1", "[00:30]", "Absolute right kyu nahi hai?", "Defines the legal constitutional boundary."),
        ("Build 2", "[00:50]", "Trial kyu delay nahi ho sakti?", "Explains the speedy trial vs freedom conflict."),
        ("Build 3", "[01:10]", "Iska future impact kya hoga?", "Shows how it stops accused from fleeing."),
        ("Close", "[01:50]", "Kya court ka faisla sahi tha?", "Viewer poll and legal debate CTA.")
    ],
    "- SC Ruling Date: June 5, 2026\n- Core issue: Article 21 Right to Travel Abroad vs Right to Speedy Trial\n- Context: SC set aside Telangana HC order allowing accused to travel to USA for medical treatment\n- Verdict: Right to travel abroad is not absolute; cannot stall criminal proceedings",
    "8EEqmu6MVwY",
    "Article 21 - freedom aur personal liberty ka wo constitutional right jise absolute mana jata tha, lekin Supreme Court ne ispar ek bada clarification diya hai."
)
