# Aayuvridhi Healthcare System

A Python healthcare search system. Enter a disease, symptom or medicine and get:
- **Patient view**: simple explanation, home care, and when to see a doctor
- **AI Doctor view**: clinical summary, possible causes, suggested tests, red flags

## How to run
1. Install requirements: `pip install requests beautifulsoup4`
2. Run: `python src/query.py`
3. Type a search such as `fever` or `swelling in teeth`

## Files
- `src/disease_db.py`: local disease database and smart search
- `src/query.py`: main search program (falls back to online medical sources)
- `src/database.py`, `src/cleaner.py`, `src/build_datasets.py`: data handling

Note: this is general health information, not a medical diagnosis.
