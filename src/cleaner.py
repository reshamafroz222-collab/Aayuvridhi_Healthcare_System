import os
import pandas as pd

def clean_and_standardize_data():
    print("Starting data cleaning and standardization pipeline...")

    # 1. Load raw datasets
    modern_path = "data/processed/modern_medicines.csv"
    ayurveda_path = "data/processed/ayurvedic_ingredients.csv"

    if not os.path.exists(modern_path) or not os.path.exists(ayurveda_path):
        print("Error: Raw dataset files not found. Run build_datasets.py first!")
        return

    df_modern = pd.read_csv(modern_path)
    df_ayurveda = pd.read_csv(ayurveda_path)

    # 2. Clean Modern Medicines Data
    # Fill missing text fields with standard placeholders and lowercase generic names for matching
    df_modern['generic_name'] = df_modern['generic_name'].fillna("Unknown").str.strip().str.title()
    df_modern['drug_class'] = df_modern['drug_class'].fillna("Unclassified")
    df_modern['precautions'] = df_modern['precautions'].fillna("None specified")

    # 3. Clean Ayurvedic Ingredients Data
    df_ayurveda['sanskrit_name'] = df_ayurveda['sanskrit_name'].fillna("Unknown").str.strip().str.title()
    df_ayurveda['botanical_name'] = df_ayurveda['botanical_name'].fillna("Unspecified")
    df_ayurveda['ayurvedic_properties'] = df_ayurveda['ayurvedic_properties'].fillna("Not documented")

    # 4. Save cleaned data back to processed folder (ready for app consumption)
    os.makedirs("data/processed", exist_ok=True)
    df_modern.to_csv("data/processed/modern_medicines_cleaned.csv", index=False)
    df_ayurveda.to_csv("data/processed/ayurvedic_ingredients_cleaned.csv", index=False)

    print("Data cleaning completed successfully! Cleaned files saved.")

if __name__ == "__main__":
    clean_and_standardize_data()