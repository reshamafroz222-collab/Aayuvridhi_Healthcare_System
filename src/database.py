import os
import sqlite3
import pandas as pd

def init_database():
    print("Initializing SQLite database for scalable app storage...")
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    db_path = "data/healthcare.db"
    
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    
    # Load cleaned CSV files
    modern_path = "data/processed/modern_medicines_cleaned.csv"
    ayurveda_path = "data/processed/ayurvedic_ingredients_cleaned.csv"
    
    if os.path.exists(modern_path):
        df_modern = pd.read_csv(modern_path)
        # Write dataframe directly to an SQL table
        df_modern.to_sql("modern_medicines", conn, if_exists="replace", index=False)
        print("✔ Loaded modern medicines into database table.")
        
    if os.path.exists(ayurveda_path):
        df_ayurveda = pd.read_csv(ayurveda_path)
        # Write dataframe directly to an SQL table
        df_ayurveda.to_sql("ayurvedic_ingredients", conn, if_exists="replace", index=False)
        print("✔ Loaded ayurvedic ingredients into database table.")
        
    conn.close()
    print(f"Database successfully built and stored at '{db_path}'!")

if __name__ == "__main__":
    init_database()