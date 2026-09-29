"""
disease_db.py  -  local disease knowledge base for Aayuvridhi Healthcare System

Put this file in the same folder as query.py (src/).

Features
  * SQLite database (data/diseases.db) created and seeded automatically
  * Smart search: names, aliases, symptoms, synonyms ("bukhar" -> fever), typo tolerance
  * Two result styles: PATIENT view (simple language) and AI DOCTOR view (clinical)
  * import_csv() to load your big dataset (build_datasets.py / generate_large_dataset.py)

Educational information only - not a diagnosis.
"""
import csv
import difflib
import os
import re
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "data", "diseases.db")

COLS = ("name", "aliases", "category", "symptoms", "description",
        "causes", "home_care", "red_flags", "doctor_type", "tests")

DISCLAIMER = ("Note: this is general health information, not a diagnosis. "
              "Please consult a qualified doctor for advice about your condition.")

# ---------------------------------------------------------------- seed data
# Lists inside a field are separated by ";"
SEED = [
    ("Fever (Pyrexia)", "fever; high temperature; bukhar; pyrexia; raised temperature",
     "General / Symptom",
     "high temperature; chills; sweating; body ache; headache; weakness; loss of appetite",
     "Body temperature above about 38 C (100.4 F). Fever is a sign that the body is fighting "
     "something, usually an infection, rather than a disease by itself.",
     "viral infections (cold, flu, dengue); bacterial infections (typhoid, urinary tract infection); "
     "malaria; heat illness; inflammatory conditions",
     "rest; drink plenty of water, ORS, soups; light clothing; lukewarm sponging; "
     "paracetamol as per the label or your doctor's advice",
     "fever above 39.5 C (103 F) or lasting more than 3 days; stiff neck; severe headache; skin rash "
     "or bleeding; confusion; trouble breathing; seizures; persistent vomiting; infant under 3 months",
     "General Physician",
     "CBC; malaria test; dengue NS1/IgM; typhoid test; urine routine; chest X-ray if cough"),

    ("Common Cold", "cold; runny nose; nazla; upper respiratory infection",
     "Respiratory",
     "runny nose; sneezing; sore throat; mild cough; blocked nose; mild fever; watery eyes",
     "A mild viral infection of the nose and throat that usually clears in 7-10 days.",
     "rhinoviruses and other respiratory viruses spread by droplets and touch",
     "rest; warm fluids; steam inhalation; saline gargles; honey-ginger tea",
     "breathing difficulty; fever over 3 days; symptoms beyond 10 days; ear pain; chest pain",
     "General Physician", "usually none; throat swab if severe"),

    ("Influenza (Flu)", "flu; seasonal flu; viral fever; influenza",
     "Respiratory",
     "sudden high fever; body ache; chills; dry cough; sore throat; fatigue; headache",
     "A contagious viral infection of the airways, more severe than a cold.",
     "influenza A and B viruses",
     "rest; fluids; paracetamol as per label; stay home to avoid spreading",
     "shortness of breath; chest pain; confusion; bluish lips; symptoms that improve then worsen; "
     "high risk groups (elderly, pregnant, chronic illness)",
     "General Physician / Pulmonologist", "rapid flu test; CBC; chest X-ray if pneumonia suspected"),

    ("Dengue Fever", "dengue; breakbone fever; dengue viral fever",
     "Infectious (mosquito-borne)",
     "sudden high fever; severe headache; pain behind the eyes; joint and muscle pain; skin rash; "
     "nausea; low platelets",
     "A viral infection spread by Aedes mosquitoes. Most cases are mild, but some become severe.",
     "dengue virus transmitted by Aedes aegypti mosquito bites",
     "rest; plenty of fluids and ORS; paracetamol only (avoid aspirin and ibuprofen)",
     "severe stomach pain; repeated vomiting; bleeding gums or nose; black stools; cold clammy skin; "
     "drowsiness; breathlessness",
     "General Physician / Infectious Disease", "NS1 antigen; dengue IgM/IgG; CBC with platelet count"),

    ("Malaria", "malaria; intermittent fever; chill and rigor fever",
     "Infectious (mosquito-borne)",
     "fever with shivering; sweating; headache; nausea; vomiting; body ache; fever in cycles",
     "A parasite infection spread by Anopheles mosquitoes, often with fever that comes in cycles.",
     "Plasmodium parasites from mosquito bites",
     "seek medical treatment early; rest; fluids; mosquito nets",
     "confusion; seizures; dark urine; jaundice; severe weakness; breathing difficulty",
     "General Physician / Infectious Disease", "malaria rapid test; peripheral blood smear; CBC"),

    ("Typhoid Fever", "typhoid; enteric fever",
     "Infectious (food/water-borne)",
     "prolonged fever; weakness; stomach pain; headache; constipation or diarrhoea; loss of appetite",
     "A bacterial infection spread through contaminated food and water, with fever that rises step by step.",
     "Salmonella Typhi from unsafe food or water",
     "antibiotics only as prescribed; fluids; soft, clean food; strict hand hygiene",
     "severe abdominal pain; blood in stools; confusion; very high fever; dehydration",
     "General Physician", "blood culture; Widal (supportive); CBC"),

    ("Gastroenteritis", "stomach flu; loose motions; diarrhoea; food poisoning; vomiting and diarrhoea",
     "Digestive",
     "loose stools; vomiting; stomach cramps; nausea; mild fever; dehydration",
     "Inflammation of the stomach and intestines, usually from infection or contaminated food.",
     "viruses; bacteria; contaminated food or water; parasites",
     "ORS and clean fluids; small light meals such as rice, banana, curd; rest",
     "blood in stools; signs of dehydration (dry mouth, very little urine, dizziness); "
     "symptoms over 2 days; infants and elderly",
     "General Physician / Gastroenterologist", "stool test; electrolytes if severe"),

    ("Migraine", "migraine; severe headache; one sided headache",
     "Neurological",
     "throbbing headache on one side; nausea; sensitivity to light and sound; visual aura",
     "A recurring neurological headache, often moderate to severe, lasting hours to days.",
     "genetic tendency; triggers such as stress, poor sleep, skipped meals, certain foods, hormones",
     "rest in a dark quiet room; hydration; regular sleep and meals; avoid known triggers",
     "sudden worst-ever headache; weakness or numbness; speech difficulty; headache after head injury; "
     "headache with fever and stiff neck",
     "Neurologist", "clinical diagnosis; CT or MRI if red flags"),

    ("Hypertension (High Blood Pressure)", "high blood pressure; bp; hypertension",
     "Cardiovascular",
     "often none; headache; dizziness; blurred vision; chest discomfort",
     "Persistently high pressure in the arteries which raises the risk of heart attack and stroke.",
     "high salt intake; obesity; stress; inactivity; family history; kidney disease",
     "reduce salt; regular exercise; healthy weight; limit alcohol; do not smoke; take medicines as prescribed",
     "chest pain; severe headache; vision loss; weakness on one side; breathlessness",
     "Physician / Cardiologist", "repeated BP readings; ECG; kidney function; lipid profile"),

    ("Type 2 Diabetes", "diabetes; sugar; high blood sugar; madhumeh; diabetes mellitus",
     "Endocrine",
     "excess thirst; frequent urination; tiredness; blurred vision; slow-healing wounds; weight change",
     "A long-term condition where the body cannot use insulin properly, causing high blood sugar.",
     "obesity; inactivity; family history; poor diet; age",
     "balanced low-sugar diet; daily walking; weight control; regular sugar checks; medicines as prescribed",
     "very high sugar with vomiting; fruity breath; confusion; foot ulcers; sudden vision loss",
     "Physician / Endocrinologist", "fasting and post-meal glucose; HbA1c; kidney and lipid tests"),

    ("Asthma", "asthma; wheezing; breathing problem; dama",
     "Respiratory",
     "wheezing; cough especially at night; chest tightness; shortness of breath",
     "A long-term condition where the airways narrow and become inflamed, causing breathing trouble.",
     "allergens; dust; smoke; cold air; exercise; infections; family history",
     "avoid triggers; use inhalers as prescribed; keep a rescue inhaler nearby",
     "severe breathlessness; unable to speak full sentences; blue lips; no relief from rescue inhaler",
     "Pulmonologist", "spirometry; peak flow; allergy tests"),

    ("Urinary Tract Infection (UTI)", "uti; burning urination; urine infection; bladder infection",
     "Urological",
     "burning while urinating; frequent urge to pass urine; cloudy or foul urine; lower abdominal pain; mild fever",
     "An infection of the bladder or urinary tract, more common in women.",
     "bacteria such as E. coli; low water intake; poor hygiene; diabetes",
     "drink plenty of water; do not hold urine; hygiene; antibiotics only if prescribed",
     "fever with back or flank pain; blood in urine; vomiting; pregnancy; symptoms in children or men",
     "General Physician / Urologist", "urine routine and culture"),

    ("Dental Abscess", "tooth abscess; swelling in teeth; swollen gum; tooth infection; toothache with swelling",
     "Dental",
     "severe toothache; swelling in gum or face; pus; bad taste; pain while chewing; sensitivity to hot or cold; fever",
     "A pocket of pus caused by a bacterial infection in a tooth or gum.",
     "untreated tooth decay; gum disease; cracked or broken tooth",
     "warm salt-water rinses; avoid very hot, cold or hard foods; over-the-counter pain relief as per label",
     "swelling spreading to face or neck; trouble swallowing or breathing; high fever; eye swelling",
     "Dentist (emergency if swelling spreads)", "dental exam; dental X-ray"),

    ("Gingivitis", "gum disease; bleeding gums; swollen gums; gum inflammation",
     "Dental",
     "red swollen gums; bleeding while brushing; bad breath; tender gums",
     "Early gum inflammation caused by plaque build-up. It is reversible with good care.",
     "poor oral hygiene; smoking; diabetes; vitamin C deficiency",
     "brush twice daily; floss; salt-water rinses; dental cleaning; stop tobacco",
     "gums pulling away from teeth; loose teeth; pus; persistent bleeding",
     "Dentist", "dental exam"),

    ("Pneumonia", "pneumonia; chest infection; lung infection",
     "Respiratory",
     "fever; cough with phlegm; chest pain; fast breathing; breathlessness; tiredness",
     "An infection that inflames the air sacs in the lungs.",
     "bacteria; viruses; fungi; weak immunity; smoking",
     "medical treatment is needed; rest; fluids; complete the prescribed antibiotics",
     "breathlessness; blue lips; confusion; chest pain; elderly, children, or chronic illness",
     "Physician / Pulmonologist", "chest X-ray; CBC; sputum test; oxygen saturation"),

    ("Anemia", "anaemia; low haemoglobin; low hb; iron deficiency; khoon ki kami",
     "Blood",
     "tiredness; pale skin; dizziness; breathlessness on exertion; headache; brittle nails; cold hands",
     "Low haemoglobin so the blood carries less oxygen. Iron deficiency is the most common cause.",
     "iron, B12 or folate deficiency; heavy periods; blood loss; chronic disease",
     "iron-rich foods (leafy greens, dates, jaggery, legumes) with vitamin C; supplements only as advised",
     "chest pain; fainting; severe breathlessness; black stools; heavy bleeding",
     "General Physician / Haematologist", "CBC; ferritin; B12; folate"),
]

# Extra words people commonly use -> words stored in the database
SYNONYMS = {
    "temperature": ["fever"], "bukhar": ["fever"], "pyrexia": ["fever"], "chills": ["fever"],
    "tooth": ["dental", "teeth"], "teeth": ["dental", "tooth"], "gum": ["gingivitis", "dental"],
    "gums": ["gingivitis", "dental"], "toothache": ["dental", "tooth"],
    "sugar": ["diabetes"], "bp": ["hypertension"], "pressure": ["hypertension"],
    "loose": ["diarrhoea", "gastroenteritis"], "motion": ["diarrhoea"], "motions": ["diarrhoea"],
    "diarrhea": ["diarrhoea"], "stomach": ["gastroenteritis"], "vomit": ["vomiting"],
    "breathless": ["breathlessness"], "breathing": ["breathlessness", "asthma"],
    "urine": ["urinary"], "peeing": ["urinary"], "swelling": ["swollen"],
    "cough": ["cold", "respiratory"], "throat": ["cold", "respiratory"],
    "tired": ["tiredness", "weakness", "anemia"], "fatigue": ["tiredness", "weakness"],
    "hb": ["haemoglobin"], "haemoglobin": ["anemia"], "hemoglobin": ["anemia"],
}

STOPWORDS = {"a", "an", "and", "in", "on", "of", "the", "my", "i", "have", "has", "is", "am",
             "with", "for", "to", "me", "it", "am", "feel", "feeling", "getting", "since", "from"}


# ---------------------------------------------------------------- database
def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the table and add the built-in diseases if the table is empty."""
    with _connect() as con:
        con.execute(
            "CREATE TABLE IF NOT EXISTS diseases ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, aliases TEXT, category TEXT, "
            "symptoms TEXT, description TEXT, causes TEXT, home_care TEXT, red_flags TEXT, "
            "doctor_type TEXT, tests TEXT)")
        if con.execute("SELECT COUNT(*) FROM diseases").fetchone()[0] == 0:
            con.executemany(
                "INSERT OR IGNORE INTO diseases (%s) VALUES (%s)" % (",".join(COLS), ",".join("?" * len(COLS))),
                SEED)


def import_csv(csv_path):
    """Load a large dataset. CSV needs at least a 'name' column; other columns from COLS are optional."""
    init_db()
    added = 0
    with _connect() as con, open(csv_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            row = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
            if not row.get("name"):
                continue
            values = [row.get(c, "") for c in COLS]
            con.execute("INSERT OR REPLACE INTO diseases (%s) VALUES (%s)"
                        % (",".join(COLS), ",".join("?" * len(COLS))), values)
            added += 1
    return added


# ---------------------------------------------------------------- search
def _stem(word):
    for suffix in ("ing", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def _tokens(text):
    return {_stem(w) for w in re.findall(r"[a-z]+", text.lower()) if w not in STOPWORDS and len(w) > 1}


def search(query, limit=5):
    """Return up to `limit` matching diseases as dicts, best match first."""
    init_db()
    q_words = [w for w in re.findall(r"[a-z]+", query.lower()) if w not in STOPWORDS]
    direct = {_stem(w) for w in q_words}
    extra = {_stem(s) for w in q_words for s in SYNONYMS.get(w, [])} - direct
    if not direct:
        return []

    with _connect() as con:
        con.row_factory = sqlite3.Row
        rows = [dict(r) for r in con.execute("SELECT * FROM diseases")]

    ranked = []
    for r in rows:
        name_t, alias_t = _tokens(r["name"]), _tokens(r["aliases"])
        symp_t, cat_t = _tokens(r["symptoms"]), _tokens(r["category"])
        text_t = _tokens(r["description"] + " " + r["causes"])
        score = 0.0
        for t in direct:
            score += 6 * (t in name_t) + 5 * (t in alias_t) + 3 * (t in symp_t) + 2 * (t in cat_t) + (t in text_t)
        for t in extra:
            score += 0.5 * ((t in name_t) * 6 + (t in alias_t) * 5 + (t in symp_t) * 3 + (t in cat_t) * 2 + (t in text_t))
        exact = [r["name"].lower()] + [a.lower() for a in _items(r["aliases"])]
        if query.lower().strip() in exact:
            score += 10  # whole-name / whole-alias match goes first
        if score > 0:
            ranked.append((score, r))

    # typo tolerance: "feveer" -> "fever"
    if not ranked:
        vocab = {}
        for r in rows:
            for t in _tokens(r["name"] + " " + r["aliases"] + " " + r["symptoms"]):
                vocab.setdefault(t, []).append(r)
        for w in direct:
            for close in difflib.get_close_matches(w, vocab.keys(), n=2, cutoff=0.8):
                for r in vocab[close]:
                    ranked.append((1.0, r))

    seen, results = set(), []
    for score, r in sorted(ranked, key=lambda x: -x[0]):
        if r["name"] not in seen:
            seen.add(r["name"])
            results.append(r)
    return results[:limit]


# ---------------------------------------------------------------- output
def _items(text):
    return [i.strip() for i in text.split(";") if i.strip()]


def _bullets(text):
    return "\n".join("   - " + i for i in _items(text)) or "   - (not available)"


def patient_view(d):
    return (
        f"\n  {d['name']}\n  " + "-" * 50 + "\n"
        f"  What it is:\n   {d['description']}\n\n"
        f"  Common signs you may notice:\n{_bullets(d['symptoms'])}\n\n"
        f"  What you can do at home:\n{_bullets(d['home_care'])}\n\n"
        f"  See a doctor urgently if:\n{_bullets(d['red_flags'])}\n\n"
        f"  Who to consult: {d['doctor_type']}\n"
    )


def doctor_view(d):
    return (
        f"\n  [AI Doctor] {d['name']}  |  {d['category']}\n  " + "-" * 50 + "\n"
        f"  Clinical summary:\n   {d['description']}\n\n"
        f"  Possible causes to consider:\n{_bullets(d['causes'])}\n\n"
        f"  Suggested investigations:\n{_bullets(d['tests'])}\n\n"
        f"  Red flags (escalate immediately):\n{_bullets(d['red_flags'])}\n\n"
        f"  Specialist: {d['doctor_type']}\n"
    )


def search_and_print(query, limit=3):
    """Print patient + AI doctor results. Returns True if something was found."""
    results = search(query, limit)
    print("\n[LOCAL AAYURVIDHI DATABASE]")
    if not results:
        print("No local matches found.")
        return False

    print(f"Found {len(results)} related result(s) for '{query}':")
    for i, d in enumerate(results, 1):
        print("\n" + "=" * 60)
        print(f"RESULT {i} of {len(results)}")
        print("=" * 60)
        print("\n  >>> PATIENT VIEW")
        print(patient_view(d))
        print("  >>> AI DOCTOR VIEW")
        print(doctor_view(d))
    print("\n" + DISCLAIMER)
    return True


if __name__ == "__main__":
    init_db()
    search_and_print(input("Enter a disease, symptom or condition: "))
