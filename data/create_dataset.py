# create_dataset.py
import pandas as pd
import numpy as np

def create_respiria_dataset(n_samples=2000):
    """
    Créer un dataset synthétique pour Respiria
    basé sur des règles médicales réalistes
    """
    np.random.seed(42)
    data = []
    
    # Profils utilisateur
    profiles = {
        0: {'name': 'Prévention', 'tolerance': 1.3},
        1: {'name': 'Asthmatique stable', 'tolerance': 1.0},
        2: {'name': 'Asthmatique sévère', 'tolerance': 0.7},
        3: {'name': 'Rémission', 'tolerance': 0.5}
    }
    
    for _ in range(n_samples):
        # Profil aléatoire
        profile = np.random.choice([0, 1, 2, 3])
        tolerance = profiles[profile]['tolerance']
        
        # Génération des valeurs capteurs
        spo2 = np.random.normal(95, 3)
        bpm = np.random.normal(75, 15)
        eco2 = np.random.normal(800, 200)
        aqi = np.random.normal(80, 40)
        temp = np.random.normal(24, 3)
        humidity = np.random.normal(55, 15)
        tvoc = np.random.normal(400, 200)
        pollen = np.random.normal(80, 40)
        
        # Calcul du score de risque basé sur les seuils médicaux
        risk_score = 0
        
        # SpO2 (saturation en oxygène)
        if spo2 < 94 * tolerance:
            risk_score += 3
        elif spo2 < 96 * tolerance:
            risk_score += 2
        elif spo2 < 98 * tolerance:
            risk_score += 1
        
        # Fréquence cardiaque
        if bpm > 100 / tolerance:
            risk_score += 3
        elif bpm > 85 / tolerance:
            risk_score += 2
        elif bpm > 75 / tolerance:
            risk_score += 1
        
        # eCO2
        if eco2 > 1200 / tolerance:
            risk_score += 3
        elif eco2 > 1000 / tolerance:
            risk_score += 2
        elif eco2 > 800 / tolerance:
            risk_score += 1
        
        # AQI (qualité de l'air)
        if aqi > 150 / tolerance:
            risk_score += 3
        elif aqi > 100 / tolerance:
            risk_score += 2
        elif aqi > 50 / tolerance:
            risk_score += 1
        
        # Température
        if temp > 28 or temp < 18:
            risk_score += 1
        
        # Humidité
        if humidity > 70 or humidity < 30:
            risk_score += 1
        
        # TVOC
        if tvoc > 700:
            risk_score += 2
        elif tvoc > 500:
            risk_score += 1
        
        # Pollen
        if pollen > 120:
            risk_score += 2
        elif pollen > 80:
            risk_score += 1
        
        # Détermination de la classe de risque
        if risk_score >= 8:
            risk_class = 2  # Élevé
        elif risk_score >= 4:
            risk_class = 1  # Moyen
        else:
            risk_class = 0  # Faible
        
        data.append({
            'user_profile': profile,
            'heart_rate_bpm': max(40, min(200, bpm)),
            'spo2': max(85, min(100, spo2)),
            'temperature_c': max(15, min(35, temp)),
            'humidity_percent': max(20, min(90, humidity)),
            'eco2_ppm': max(400, min(2000, eco2)),
            'tvoc_ppb': max(0, min(1000, tvoc)),
            'aqi': max(0, min(250, aqi)),
            'pollen_level': max(0, min(200, pollen)),
            'risk_class': risk_class
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("🔄 Création du dataset Respiria...")
    df = create_respiria_dataset(n_samples=2000)
    
    # Sauvegarder
    df.to_csv('respiria_dataset.csv', index=False)
    
    print(f"✅ Dataset créé : {len(df)} échantillons")
    print(f"\n📊 Distribution des classes :")
    print(df['risk_class'].value_counts().sort_index())
    print(f"\n📊 Distribution par profil :")
    print(df['user_profile'].value_counts().sort_index())
    print(f"\n💾 Sauvegardé dans : respiria_dataset.csv")