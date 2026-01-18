# models/train_model.py
import pandas as pd
import numpy as np
import joblib
import os
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from tabpfn import TabPFNClassifier
from huggingface_hub import login
import warnings
warnings.filterwarnings('ignore')

# Charger les variables d'environnement depuis .env
try:
    from dotenv import load_dotenv
    # Chercher .env dans le dossier parent (racine du projet)
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Variables chargées depuis {env_path}")
    else:
        # Chercher aussi dans venv/.env
        env_path_venv = Path(__file__).parent.parent / 'venv' / '.env'
        if env_path_venv.exists():
            load_dotenv(env_path_venv)
            print(f"✅ Variables chargées depuis {env_path_venv}")
except ImportError:
    print("⚠️ python-dotenv non installé, utilisation des variables système")

# Configuration des chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
MODEL_DIR = BASE_DIR / 'models'

# Token HuggingFace depuis variable d'environnement
HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN or HF_TOKEN == "YOUR_HUGGINGFACE_TOKEN":
    print("⚠️ HF_TOKEN non défini! Définissez-le dans .env ou comme variable d'environnement")

def train_respiria_model():
    """Entraîne le modèle Respiria avec TabPFN"""
    
    print("="*70)
    print("🚀 ENTRAÎNEMENT DU MODÈLE RESPIRIA ML")
    print("="*70)
    
    # 1. Connexion HuggingFace
    print("\n1️⃣ Connexion à HuggingFace...")
    if 'HF_TOKEN' in os.environ:
        del os.environ['HF_TOKEN']
    login(token=HF_TOKEN)
    print("✅ Connecté")
    
    # 2. Chargement du dataset
    print("\n2️⃣ Chargement du dataset...")
    dataset_path = DATA_DIR / 'respiria_dataset.csv'
    
    if not dataset_path.exists():
        print(f"❌ Fichier non trouvé : {dataset_path}")
        print(f"📁 Cherche dans : {DATA_DIR}")
        print(f"📂 Fichiers disponibles : {list(DATA_DIR.glob('*.csv'))}")
        return None, None
    
    df = pd.read_csv(dataset_path)
    print(f"✅ {len(df)} échantillons chargés")
    print(f"📊 Shape : {df.shape}")
    
    # 3. Feature Engineering
    print("\n3️⃣ Feature Engineering...")
    X = df.drop('risk_class', axis=1)
    y = df['risk_class']
    
    # Interactions profil × capteurs (crucial pour différencier les profils)
    X['profile_x_hr'] = X['heart_rate_bpm'] * X['user_profile']
    X['profile_x_spo2'] = X['spo2'] * X['user_profile']
    X['profile_x_eco2'] = X['eco2_ppm'] * X['user_profile']
    X['profile_x_aqi'] = X['aqi'] * X['user_profile']
    
    print(f"✅ {X.shape[1]} features créées")
    print(f"📋 Features : {list(X.columns)}")
    
    # 4. Normalisation
    print("\n4️⃣ Normalisation...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns)
    print("✅ Normalisation terminée")
    
    # 5. Split
    print("\n5️⃣ Train/Test split...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"✅ Train: {len(X_train)} | Test: {len(X_test)}")
    
    # 6. Sous-échantillonnage pour TabPFN
    print("\n6️⃣ Préparation pour TabPFN...")
    sample_size = min(1000, len(X_train))
    X_train_sample, _, y_train_sample, _ = train_test_split(
        X_train, y_train,
        train_size=sample_size,
        stratify=y_train,
        random_state=42
    )
    print(f"✅ {len(X_train_sample)} échantillons pour l'entraînement")
    
    # 7. Entraînement
    print("\n7️⃣ Entraînement TabPFN...")
    print("⏳ Cela prend 2-5 minutes...")
    
    model = TabPFNClassifier(
        device="cpu",
        n_estimators=32,
        ignore_pretraining_limits=True
    )
    
    model.fit(X_train_sample, y_train_sample)
    print("✅ Modèle entraîné !")
    
    # 8. Évaluation
    print("\n8️⃣ Évaluation...")
    y_pred = model.predict(X_test)
    
    print("\n" + "="*70)
    print("📊 RAPPORT DE CLASSIFICATION")
    print("="*70)
    report = classification_report(
        y_test, y_pred,
        target_names=['Risque faible', 'Risque modéré', 'Risque élevé'],
        digits=3
    )
    print(report)
    
    # Matrice de confusion
    cm = confusion_matrix(y_test, y_pred)
    print("\n📊 MATRICE DE CONFUSION")
    print(cm)
    
    # 9. Sauvegarde
    print("\n9️⃣ Sauvegarde...")
    
    # Créer le dossier models s'il n'existe pas
    MODEL_DIR.mkdir(exist_ok=True)
    
    joblib.dump(model, MODEL_DIR / 'respiria_model.pkl')
    joblib.dump(scaler, MODEL_DIR / 'respiria_scaler.pkl')
    joblib.dump(list(X.columns), MODEL_DIR / 'respiria_features.pkl')
    
    print(f"✅ Modèle sauvegardé : {MODEL_DIR / 'respiria_model.pkl'}")
    print(f"✅ Scaler sauvegardé : {MODEL_DIR / 'respiria_scaler.pkl'}")
    print(f"✅ Features sauvegardées : {MODEL_DIR / 'respiria_features.pkl'}")
    
    # 10. Test rapide
    print("\n🔟 Test rapide du modèle...")
    test_data = pd.DataFrame([{
        'user_profile': 1,
        'heart_rate_bpm': 95,
        'spo2': 93,
        'temperature_c': 26,
        'humidity_percent': 65,
        'eco2_ppm': 1100,
        'tvoc_ppb': 500,
        'aqi': 110,
        'pollen_level': 100,
        'profile_x_hr': 95,
        'profile_x_spo2': 93,
        'profile_x_eco2': 1100,
        'profile_x_aqi': 110
    }])
    
    test_scaled = scaler.transform(test_data)
    prediction = model.predict(test_scaled)[0]
    probas = model.predict_proba(test_scaled)[0]
    
    risk_labels = {0: 'Faible', 1: 'Modéré', 2: 'Élevé'}
    print(f"   Risque prédit : {risk_labels[prediction]}")
    print(f"   Probabilités : {probas}")
    
    print("\n" + "="*70)
    print("✅ ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS")
    print("="*70)
    
    return model, scaler

if __name__ == "__main__":
    model, scaler = train_respiria_model()