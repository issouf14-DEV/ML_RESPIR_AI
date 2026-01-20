import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from data_collector import RespiriaDataCollector
from respiria_ai_predictor import RespiriaAIPredictor

print("=" * 80)
print("TEST COMPLET - 4 PROFILS AVEC DONNEES REELLES UBIDOTS")
print("=" * 80)

# Profils
PROFILES = {
    0: "Prevention",
    1: "Stable", 
    2: "Severe",
    3: "Remission"
}

# Créer le collecteur
collector = RespiriaDataCollector()

print("\n📊 RECUPERATION DES DONNEES EN TEMPS REEL...")
print("-" * 80)

# Récupérer données Ubidots
sensor_data = collector.get_ubidots_direct()

print("✓ Donnees capteurs Ubidots:")
print(f"  SpO2: {sensor_data['spo2']}%")
print(f"  BPM: {sensor_data['heart_rate']}")
print(f"  Temperature: {sensor_data['temperature_sensor']}°C")
print(f"  Humidite: {sensor_data['humidity_sensor']}%")
print(f"  eCO2: {sensor_data['eco2_ppm']} ppm")
print(f"  TVOC: {sensor_data['tvoc_ppb']} ppb")
print(f"  Fumee: {'OUI' if sensor_data['smoke_detected'] else 'NON'}")

# Récupérer données complètes
print("\n📡 Recuperation des donnees externes...")
base_data = collector.collect_all_data(user_id=1)

print(f"✓ Donnees collectees: {len(base_data)} champs")

# Créer le prédicteur
predictor = RespiriaAIPredictor()

print("\n" + "=" * 80)
print("TEST DES 4 PROFILS UTILISATEURS")
print("=" * 80)

for profile_id, profile_name in PROFILES.items():
    print(f"\n{'-' * 80}")
    print(f"PROFIL {profile_id}: {profile_name.upper()}")
    print(f"{'-' * 80}")
    
    # Copier les données et ajouter le profil
    data = base_data.copy()
    data['profile_id'] = profile_id
    
    # Faire la prédiction
    try:
        result = predictor.predict(data)
        
        # Extraire les résultats
        score = result.get('overall_risk_score', result.get('score', 0))
        level = result.get('risk_level', 'N/A')
        factors = result.get('risk_factors', result.get('factors', []))
        recs = result.get('recommendations', [])
        
        # Afficher le résultat
        print(f"\nResultat:")
        print(f"  Score de risque: {score}/100")
        print(f"  Niveau: {level}")
        
        print(f"\nFacteurs de risque ({len(factors)}):")
        for factor in factors[:5]:  # Top 5
            name = factor.get('name', 'N/A')
            value = factor.get('value', 'N/A')
            pct = factor.get('contribution_percent', factor.get('percentage', 0))
            print(f"  - {name}: {value} -> {pct}%")
        
        print(f"\nRecommandations:")
        for i, rec in enumerate(recs[:3], 1):  # Top 3
            print(f"  {i}. {rec}")
            
    except Exception as e:
        print(f"Erreur: {e}")

print("\n" + "=" * 80)
print("VERIFICATION DETECTION FUMEE")
print("=" * 80)

if sensor_data['smoke_detected']:
    print(f"ALERTE FUMEE DETECTEE!")
    print(f"   eCO2: {sensor_data['eco2_ppm']} ppm")
    print(f"   TVOC: {sensor_data['tvoc_ppb']} ppb")
else:
    print(f"AUCUNE FUMEE DETECTEE")
    print(f"   eCO2: {sensor_data['eco2_ppm']} ppm (seuil: > 4000)")
    print(f"   TVOC: {sensor_data['tvoc_ppb']} ppb (seuil: > 2000)")
    print(f"   Combinaison: eCO2 > 4000 ET TVOC > 1000")

print("\n" + "=" * 80)
print("TESTS TERMINES")
print("=" * 80)
