import os
import pandas as pd

# Ensure data/processed directory exists
os.makedirs("data/processed", exist_ok=True)

def create_datasets():
    print("Generating expanded mock datasets for stress testing...")

    # 1. Expanded Modern Medicines Dataset
    modern_medicines = pd.DataFrame([
        {
            "medicine_id": "MM_001",
            "medicine_name": "Crocin 650",
            "generic_name": "Paracetamol",
            "active_ingredient": "Paracetamol",
            "drug_class": "Analgesic / Antipyretic",
            "dosage_form": "Tablet",
            "common_indications": "Fever, Mild to moderate pain",
            "precautions": "Monitor liver function in high doses",
            "source_name": "OpenFDA / RxNorm"
        },
        {
            "medicine_id": "MM_002",
            "medicine_name": "Disprin",
            "generic_name": "Aspirin",
            "active_ingredient": "Acetylsalicylic Acid",
            "drug_class": "NSAID / Antiplatelet",
            "dosage_form": "Effervescent Tablet",
            "common_indications": "Headache, Pain relief, Vascular protection",
            "precautions": "Avoid in children with viral infections (Reye's syndrome)",
            "source_name": "OpenFDA / RxNorm"
        },
        {
            "medicine_id": "MM_003",
            "medicine_name": "Augmentin 625 Duo",
            "generic_name": "Amoxicillin and Potassium Clavulanate",
            "active_ingredient": "Amoxicillin / Clavulanate Potassium",
            "drug_class": "Penicillin-class Antibiotic",
            "dosage_form": "Tablet",
            "common_indications": "Bacterial infections, Respiratory tract infections",
            "precautions": "Check for penicillin allergy before administration",
            "source_name": "OpenFDA / RxNorm"
        },
        {
            "medicine_id": "MM_004",
            "medicine_name": "Cetirizine 10mg",
            "generic_name": "Cetirizine Hydrochloride",
            "active_ingredient": "Cetirizine",
            "drug_class": "Antihistamine",
            "dosage_form": "Tablet",
            "common_indications": "Allergic rhinitis, Urticaria, Itching",
            "precautions": "May cause mild drowsiness",
            "source_name": "OpenFDA / RxNorm"
        }
    ])
    modern_medicines.to_csv("data/processed/modern_medicines.csv", index=False)

    # 2. Expanded Ayurveda Dataset
    ayurvedic_ingredients = pd.DataFrame([
        {
            "ayurveda_id": "AY_001",
            "sanskrit_name": "Haridra",
            "common_name": "Turmeric",
            "botanical_name": "Curcuma longa",
            "synonyms": "Haldi, Gauri",
            "ayurvedic_properties": "Rasa: Tikta, Katu; Guna: Ruksha",
            "traditional_uses": "Vrana Shodhana (Wound cleansing), Anti-inflammatory",
            "formulations": "Haridra Khanda",
            "source_name": "Ayush Medicinal Plants Database"
        },
        {
            "ayurveda_id": "AY_002",
            "sanskrit_name": "Ashwagandha",
            "common_name": "Indian Ginseng",
            "botanical_name": "Withania somnifera",
            "synonyms": "Winter Cherry, Varahadi",
            "ayurvedic_properties": "Rasa: Tikta, Kashaya; Guna: Snigdha",
            "traditional_uses": "Balya (Strength-promoting), Rasayana (Rejuvenation)",
            "formulations": "Ashwagandharishta",
            "source_name": "Ayush Medicinal Plants Database"
        },
        {
            "ayurveda_id": "AY_003",
            "sanskrit_name": "Tulsi",
            "common_name": "Holy Basil",
            "botanical_name": "Ocimum sanctum",
            "synonyms": "Surasa, Bhutagni",
            "ayurvedic_properties": "Rasa: Katu, Tikta; Guna: Laghu, Ruksha",
            "traditional_uses": "Kshapana (Cough relief), Jvarahara (Fever reduction)",
            "formulations": "Tulsi Swasa",
            "source_name": "Ayush Medicinal Plants Database"
        },
        {
            "ayurveda_id": "AY_004",
            "sanskrit_name": "Brahmi",
            "common_name": "Waterhyssop",
            "botanical_name": "Bacopa monnieri",
            "synonyms": "Mandukaparni, Sarasvati",
            "ayurvedic_properties": "Rasa: Tikta, Kashaya; Guna: Laghu",
            "traditional_uses": "Medhya (Cognition and memory enhancement)",
            "formulations": "Brahmi Ghrita",
            "source_name": "Ayush Medicinal Plants Database"
        }
    ])
    ayurvedic_ingredients.to_csv("data/processed/ayurvedic_ingredients.csv", index=False)

    print("Expanded mock datasets successfully created in 'data/processed/'!")

if __name__ == "__main__":
    create_datasets()