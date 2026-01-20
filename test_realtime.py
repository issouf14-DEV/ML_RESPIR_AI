import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from data_collector import RespiriaDataCollector
from respiria_ai_predictor import RespiriaAIPredictor
import json

print("=" * 70)
print("TEST API AVEC VOS VRAIES DONNEES UBIDOTS")
print("=" * 70)

# Créer le collecteur de données
collector = RespiriaDataCollector()

# Profil de test (Stable = profil 1)
test_profile = 1

print(f"\n📊 Récupération des données en temps réel depuis Ubidots...")
print("-" * 70)

# Récupérer les données réelles
try:
    sensor_data = collector.get_ubidots_direct()
    
    print("✓ Données récupérées:")
    print(f"  SpO2: {sensor_data['spo2']}%")
    print(f"  BPM: {sensor_data['heart_rate']}")
    print(f"  Température: {sensor_data['temperature_sensor']}°C")
    print(f"  Humidité: {sensor_data['humidity_sensor']}%")
    print(f"  eCO2: {sensor_data['eco2_ppm']} ppm")
    print(f"  TVOC: {sensor_data['tvoc_ppb']} ppb")
    print(f"  Fumée détectée: {sensor_data['smoke_detected']}")
    
    # Récupérer données externes
    print("\n📡 Récupération des données externes (météo, AQI)...")
    external_data = collector.collect_all_data(user_id=1)  # User ID de test
    
    # Ajouter le profil dans les données
    external_data['profile_id'] = test_profile
    
    print(f"  Données collectées: {len(external_data)} champs")
    
    # Créer le prédicteur
    predictor = RespiriaAIPredictor()
    
    # Faire la prédiction avec les vraies données
    print(f"\n🤖 PRÉDICTION RESPIRIA AI (Profil {test_profile})...")
    print("-" * 70)
    
    result = predictor.predict(external_data)
    
    print(f"\n🎯 RÉSULTAT:")
    print(f"  Score de risque: {result.get('overall_risk_score', result.get('risk_score', 'N/A'))}/100")
    print(f"  Niveau: {result.get('risk_level', 'N/A')}")
    
    print(f"\n📋 Détails des facteurs:")
    factors = result.get('risk_factors', result.get('factors', []))
    for factor in factors:
        print(f"  - {factor.get('name', 'N/A')}: {factor.get('value', 'N/A')} → {factor.get('contribution_percent', factor.get('percentage', 0))}% du risque")
        if factor.get('message'):
            print(f"    {factor['message']}")
    
    print(f"\n💡 RECOMMANDATIONS:")
    recs = result.get('recommendations', [])
    for i, rec in enumerate(recs, 1):
        print(f"  {i}. {rec}")
    
    # Vérifier fumée
    print("\n" + "=" * 70)
    if sensor_data['smoke_detected']:
        print("⚠️  ALERTE: FUMÉE DÉTECTÉE (eCO2={}, TVOC={})".format(
            sensor_data['eco2_ppm'], sensor_data['tvoc_ppb']))
    else:
        print("✅ AUCUNE FUMÉE DÉTECTÉE (eCO2={} ppm, TVOC={} ppb)".format(
            sensor_data['eco2_ppm'], sensor_data['tvoc_ppb']))
    print("=" * 70)
    
except Exception as e:
    print(f"\n✗ Erreur: {e}")
    import traceback
    traceback.print_exc()
