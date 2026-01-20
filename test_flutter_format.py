import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from data_collector import RespiriaDataCollector
from respiria_ai_predictor import RespiriaAIPredictor
import json

print("=" * 80)
print("FORMAT JSON ENVOYE PAR L'API AU FRONTEND FLUTTER")
print("=" * 80)

PROFILES = {
    0: "Prevention",
    1: "Stable",
    2: "Severe",
    3: "Remission"
}

collector = RespiriaDataCollector()
predictor = RespiriaAIPredictor()

# Collecter les données
print("\nRecuperation des donnees Ubidots...")
sensor_data = collector.get_ubidots_direct()
base_data = collector.collect_all_data(user_id=1)

print(f"Capteurs: SpO2={sensor_data['spo2']}%, BPM={sensor_data['heart_rate']}")
print(f"Fumee: {'OUI' if sensor_data['smoke_detected'] else 'NON'}")

for profile_id, profile_name in PROFILES.items():
    print(f"\n{'▓' * 80}")
    print(f"PROFIL {profile_id}: {profile_name}")
    print(f"{'▓' * 80}")
    
    # Préparer les données
    data = base_data.copy()
    data['profile_id'] = profile_id
    
    # Faire la prédiction (comme dans l'API)
    result = predictor.predict(data)
    
    # Extraire (comme dans app.py)
    prediction = result.get('prediction', {})
    risk_level = prediction.get('risk_level', 'low').upper()
    risk_score = prediction.get('risk_score', 0)
    confidence = prediction.get('confidence', 0.96)
    should_notify = prediction.get('should_notify', False)
    
    risk_factors = result.get('risk_factors', [])
    recommendations = result.get('recommendations', {})
    profile_context = result.get('profile_context', {})
    
    # Format envoyé au Flutter (simplifié)
    flutter_response = {
        'success': True,
        'prediction': {
            'risk_level': risk_level,
            'risk_score': round(risk_score, 1),
            'confidence': round(confidence * 100),
            'should_notify': should_notify
        },
        'factors': risk_factors,
        'recommendations': recommendations,
        'profile_context': profile_context,
        'sensors': {
            'spo2': sensor_data['spo2'],
            'heart_rate': sensor_data['heart_rate'],
            'eco2': sensor_data['eco2_ppm'],
            'tvoc': sensor_data['tvoc_ppb'],
            'smoke_detected': sensor_data['smoke_detected']
        }
    }
    
    print(f"\nRESULTAT:")
    print(f"  Score: {flutter_response['prediction']['risk_score']}/100")
    print(f"  Niveau: {flutter_response['prediction']['risk_level']}")
    print(f"  Confiance: {flutter_response['prediction']['confidence']}%")
    print(f"  Notification: {flutter_response['prediction']['should_notify']}")
    
    print(f"\nPROFIL:")
    print(f"  Nom: {profile_context.get('name')}")
    print(f"  Message: {profile_context.get('message')}")
    print(f"  Conseil: {profile_context.get('specific_advice')}")
    
    print(f"\nFACTEURS ({len(risk_factors)}):")
    for f in risk_factors[:3]:
        print(f"  - {f.get('factor')}: {f.get('value')} ({f.get('contribution_percent')}%)")
    
    print(f"\nRECOMMANDATIONS:")
    imm = recommendations.get('immediate', [])
    prev = recommendations.get('preventive', [])
    env = recommendations.get('environmental', [])
    print(f"  Immediates: {len(imm)}")
    for r in imm:
        print(f"    • {r}")
    print(f"  Preventives: {len(prev)}")
    for r in prev:
        print(f"    • {r}")
    print(f"  Environnementales: {len(env)}")
    for r in env:
        print(f"    • {r}")

print(f"\n{'=' * 80}")
print("JSON COMPLET (Profil 1):")
print(f"{'=' * 80}\n")

data = base_data.copy()
data['profile_id'] = 1
result = predictor.predict(data)
prediction = result.get('prediction', {})
flutter_final = {
    'success': True,
    'prediction': {
        'risk_level': prediction.get('risk_level', 'low').upper(),
        'risk_score': round(prediction.get('risk_score', 0), 1),
        'confidence': round(prediction.get('confidence', 0.96) * 100),
        'should_notify': prediction.get('should_notify', False)
    },
    'factors': result.get('risk_factors', []),
    'recommendations': result.get('recommendations', {}),
    'profile_context': result.get('profile_context', {}),
    'sensors': {
        'spo2': sensor_data['spo2'],
        'heart_rate': sensor_data['heart_rate'],
        'eco2': sensor_data['eco2_ppm'],
        'tvoc': sensor_data['tvoc_ppb'],
        'smoke_detected': sensor_data['smoke_detected']
    }
}

print(json.dumps(flutter_final, indent=2, ensure_ascii=False))
