import os
import pandas as pd

def generate_datasets():
    print("Generating fully expanded healthcare dataset with comprehensive medical categories...")
    os.makedirs("data/processed", exist_ok=True)

    categories = [
        {
            "cat": "Ophthalmic", 
            "symptoms": [
                "Redness in Eyes", "Itchy Eyes", "Dry Eyes", "Eye Strain", 
                "Blurred Vision", "Watery Eyes", "Eye Irritation", "Eye Fatigue"
            ]
        },
        {
            "cat": "Dental", 
            "symptoms": [
                "Swelling in Gums", "Toothache", "Bleeding Gums", "Mouth Ulcers", 
                "Sensitive Teeth", "Plaque", "Gum Inflammation", "Bad Breath"
            ]
        },
        {
            "cat": "Gastrointestinal", 
            "symptoms": [
                "Stomachache", "Acidity", "Indigestion", "Nausea", "Vomiting", 
                "Bloating", "Constipation", "Diarrhea", "Gastritis", "Acid Reflux"
            ]
        },
        {
            "cat": "Respiratory", 
            "symptoms": [
                "Cough", "Cold", "Shortness of Breath", "Wheezing", "Sore Throat", 
                "Chest Congestion", "Sinusitis", "Bronchitis", "Asthma Flare"
            ]
        },
        {
            "cat": "Neurological", 
            "symptoms": [
                "Headache", "Migraine", "Anxiety", "Stress", "Insomnia", 
                "Brain Fog", "Fatigue", "Memory Loss", "Mild Vertigo"
            ]
        },
        {
            "cat": "Musculoskeletal", 
            "symptoms": [
                "Joint Pain", "Muscle Soreness", "Arthritis Stiffness", "Back Pain", 
                "Neck Pain", "Inflammation", "Sprains", "Muscle Spasms"
            ]
        },
        {
            "cat": "Dermatological", 
            "symptoms": [
                "Skin Itching", "Acne", "Eczema Flare", "Dry Skin", "Wounds", 
                "Rashes", "Hives", "Minor Cuts", "Boils", "Lump", "Skin Growth"
            ]
        },
        {
            "cat": "Cardiovascular", 
            "symptoms": [
                "Chest Pain", "Palpitations", "High Blood Pressure", "Shortness of Breath on Exertion", 
                "Dizziness", "Swelling in Legs", "Fatigue", "Rapid Heart Rate"
            ]
        },
        {
            "cat": "General Medicine", 
            "symptoms": [
                "Fever", "Body Ache", "Chills", "General Weakness", "Loss of Appetite", 
                "Sweating", "Lump", "Swollen Lymph Nodes", "Unexplained Weight Loss"
            ]
        },
        {
            "cat": "Endocrine & Metabolic", 
            "symptoms": [
                "Weight Gain", "Weight Loss", "Excessive Thirst", "Frequent Urination", 
                "Fatigue", "Mood Swings", "Heat Intolerance", "Cold Intolerance"
            ]
        }
    ]

    modern_records = []
    ayurveda_records = []

    id_counter = 1
    for cat_data in categories:
        cat_name = cat_data["cat"]
        for symptom in cat_data["symptoms"]:
            for variant in range(1, 8):
                m_id = f"MM_{id_counter:03d}"
                a_id = f"AY_{id_counter:03d}"
                
                modern_records.append({
                    "medicine_id": m_id,
                    "medicine_name": f"{cat_name[:3]}-{symptom.replace(' ', '')}-Rx {variant}",
                    "generic_name": f"Compound formulation for {symptom} Type {variant}",
                    "active_ingredient": f"Active Therapeutic Agent {id_counter}",
                    "drug_class": f"{cat_name} Therapeutic Agent",
                    "dosage_form": "Tablet / Capsule / Syrup / Topical",
                    "common_indications": f"{symptom}, Associated {cat_name.lower()} disorders, Related syndromes",
                    "precautions": "Follow clinical guidelines; consult a licensed medical professional if symptoms persist.",
                    "source_name": "Unified Healthcare Clinical Database"
                })

                ayurveda_records.append({
                    "ayurveda_id": a_id,
                    "sanskrit_name": f"Herbo{cat_name[:3]}{variant}",
                    "common_name": f"Traditional Remedy for {symptom} {variant}",
                    "botanical_name": f"Botanicus {symptom.lower().replace(' ', '_')} var{variant}",
                    "synonyms": f"Natural {symptom} Relief, Herbocare {variant}",
                    "ayurvedic_properties": "Rasa: Tikta, Katu, Madhura; Guna: Laghu, Snigdha",
                    "traditional_uses": f"Shamana therapy for {symptom}, Balya, Balancing {cat_name.lower()} doshas",
                    "formulations": f"Traditional {cat_name} Formulation {variant}",
                    "source_name": "Ayush Global Medicinal Plants Registry"
                })
                id_counter += 1

    df_modern = pd.DataFrame(modern_records)
    df_ayurveda = pd.DataFrame(ayurveda_records)

    df_modern.to_csv("data/processed/modern_medicines.csv", index=False)
    df_ayurveda.to_csv("data/processed/ayurvedic_ingredients.csv", index=False)

    print(f"Successfully generated {len(df_modern)} Modern and {len(df_ayurveda)} Ayurvedic records across expanded categories!")

if __name__ == "__main__":
    generate_datasets()