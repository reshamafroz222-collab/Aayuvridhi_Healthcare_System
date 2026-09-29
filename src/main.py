import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Unified Healthcare Data Intelligence System",
    description="Backend API bridging Modern Pharmacology and Ayurvedic Medicine.",
    version="1.0.0"
)

# Enable CORS so your future frontend app can communicate smoothly without glitches
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    db_path = "data/healthcare.db"
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="Database not initialized. Run pipeline scripts first.")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "Unified Healthcare Data Intelligence System",
        "documentation": "/docs"
    }

@app.get("/search")
def search_healthcare(q: str = Query(..., description="Search term for symptoms, diseases, or herbs")):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Split query into keywords for flexible multi-word token matching
    keywords = [kw.strip() for kw in q.split() if len(kw.strip()) > 1]
    if not keywords:
        keywords = [q.strip()]

    # Search Modern Medicines
    modern_query = "SELECT DISTINCT medicine_id, medicine_name, generic_name, drug_class, common_indications, precautions FROM modern_medicines WHERE "
    modern_conditions = []
    modern_params = []
    for kw in keywords:
        modern_conditions.append("(medicine_name LIKE ? OR generic_name LIKE ? OR common_indications LIKE ?)")
        modern_params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%"])
    modern_query += " OR ".join(modern_conditions)
    
    cursor.execute(modern_query, modern_params)
    modern_rows = [dict(row) for row in cursor.fetchall()]

    # Search Ayurvedic Ingredients
    ayurveda_query = "SELECT DISTINCT ayurveda_id, sanskrit_name, common_name, botanical_name, traditional_uses, ayurvedic_properties FROM ayurvedic_ingredients WHERE "
    ayurveda_conditions = []
    ayurveda_params = []
    for kw in keywords:
        ayurveda_conditions.append("(sanskrit_name LIKE ? OR common_name LIKE ? OR traditional_uses LIKE ? OR synonyms LIKE ?)")
        ayurveda_params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%"])
    ayurveda_query += " OR ".join(ayurveda_conditions)

    cursor.execute(ayurveda_query, ayurveda_params)
    ayurveda_rows = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "query": q,
        "modern_medicines_count": len(modern_rows),
        "modern_medicines": modern_rows[:10],  # Return top 10 matches
        "ayurvedic_ingredients_count": len(ayurveda_rows),
        "ayurvedic_ingredients": ayurveda_rows[:10]
    }