import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from data_collector import RespiriaDataCollector
from respiria_ai_predictor import RespiriaAIPredictor
import json

print("=" * 80)
print("TEST 4 PROFILS - PREDICTIONS ET RECOMMANDATIONS PERSONNALISEES")
print("=" * 80)

PROFILES = {
    0: "Prevention (Asthme leger - pas de symptomes)",
    1: "Stable (Asthme controle avec traitement)",
    2: "Severe (Asthme non controle - crises frequentes)",
    3: "Remission (Ancien asthmatique - surveillance)"
}

# Récupérer les données
collector = RespiriaDataCollector()
base_data = collector.collect_all_data(user_id=1)

print("\n📊 DONNEES UBIDOTS EN TEMPS REEL:")
sensor = collector.get_ubidots_direct()
print(f"  SpO2: {sensor['spo2']}% | BPM: {sensor['heart_rate']}")
print(f"  eCO2: {sensor['eco2_ppm']} ppm | TVOC: {sensor['tvoc_ppb']} ppb")
print(f"  Fumee: {'OUI' if sensor['smoke_detected'] else 'NON'}")

predictor = RespiriaAIPredictor()

print("\n" + "=" * 80)

for profile_id, profile_desc in PROFILES.items():
    print("\n" + "▓" * 80)
    print(f"  PROFIL {profile_id}: {profile_desc}")
    print("▓" * 80)
    
    # Préparer les données avec le profil
    data = base_data.copy()
    data['profile_id'] = profile_id
    
    # Faire la prédiction
    result = predictor.predict(data)
    
    # Extraire les informations
    pred = result.get('prediction', {})
    risk_score = pred.get('risk_score', 0)
    risk_level = pred.get('risk_level', 'N/A').upper()
    should_notify = pred.get('should_notify', False)
    confidence = pred.get('confidence', 0)
    
    # Contexte du profil
    profile_ctx = result.get('profile_context', {})
    profile_name = profile_ctx.get('name', 'N/A')
    baseline = profile_ctx.get('baseline_risk', 'N/A')
    message = profile_ctx.get('message', '')
    advice = profile_ctx.get('specific_advice', '')
    alert = profile_ctx.get('alert_level', 'N/A')
    
    # Facteurs de risque
    factors = result.get('risk_factors', [])
    
    # Recommandations
    recs = result.get('recommendations', {})
    immediate = recs.get('immediate', [])
    preventive = recs.get('preventive', [])
    environmental = recs.get('environmental', [])
    
    print(f"\n🎯 PREDICTION:")
    print(f"  Score de risque: {risk_score}/100")
    print(f"  Niveau: {risk_level}")
    print(f"  Confiance: {confidence*100:.0f}%")
    print(f"  Notification: {'OUI' if should_notify else 'NON'}")
    
    print(f"\n👤 PROFIL:")
    print(f"  Nom: {profile_name}")
    print(f"  Risque de base: {baseline}")
    print(f"  Niveau d'alerte: {alert}")
    print(f"  Message: {message}")
    print(f"  Conseil: {advice}")
    
    print(f"\n📊 FACTEURS DE RISQUE ({len(factors)}):")
    if factors:
        for i, factor in enumerate(factors[:5], 1):
            f_name = factor.get('factor', 'N/A')
            f_value = factor.get('value', 'N/A')
            f_pct = factor.get('contribution_percent', 0)
            f_msg = factor.get('message', '')
            print(f"  {i}. {f_name}: {f_value} -> {f_pct:.1f}% du risque")
            if f_msg:
                print(f"     {f_msg}")
    else:
        print("  Aucun facteur de risque detecte")
    
    print(f"\n💡 RECOMMANDATIONS:")
    
    if immediate:
        print("  🚨 IMMEDIATES:")
        for i, rec in enumerate(immediate, 1):
            print(f"    {i}. {rec}")
    else:
        print("  🚨 IMMEDIATES: Aucune")
    
    if preventive:
        print("  🛡️  PREVENTIVES:")
        for i, rec in enumerate(preventive, 1):
            print(f"    {i}. {rec}")
    else:
        print("  🛡️  PREVENTIVES: Aucune")
    
    if environmental:
        print("  🌍 ENVIRONNEMENTALES:")
        for i, rec in enumerate(environmental, 1):
            print(f"    {i}. {rec}")
    else:
        print("  🌍 ENVIRONNEMENTALES: Aucune")
    
    total_recs = len(immediate) + len(preventive) + len(environmental)
    if total_recs == 0:
        print("\n  ✅ Situation normale - Aucune action requise")

print("\n" + "=" * 80)
print("VERIFICATION FUMEE:")
print("=" * 80)
if sensor['smoke_detected']:
    print(f"⚠️  FUMEE DETECTEE (eCO2: {sensor['eco2_ppm']}, TVOC: {sensor['tvoc_ppb']})")
else:
    print(f"✅ Aucune fumee (eCO2: {sensor['eco2_ppm']} ppm, TVOC: {sensor['tvoc_ppb']} ppb)")

print("\n" + "=" * 80)
print("TESTS TERMINES")
print("=" * 80)
