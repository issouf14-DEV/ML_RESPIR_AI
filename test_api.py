import requests
import json

print("=" * 80)
print("TEST API ML - FORMAT ENVOYE AU FRONTEND FLUTTER")
print("=" * 80)

# URL de l'API (local)
API_URL = "http://localhost:5000/api/v1/predict"

# Test pour les 4 profils
PROFILES = {
    0: "Prevention",
    1: "Stable",
    2: "Severe",
    3: "Remission"
}

for profile_id, profile_name in PROFILES.items():
    print(f"\n{'=' * 80}")
    print(f"PROFIL {profile_id}: {profile_name}")
    print(f"{'=' * 80}")
    
    # Requête au format Flutter
    payload = {
        "user_id": 1,
        "profile_id": profile_id,
        "location": {
            "latitude": 5.3599,
            "longitude": -4.0083
        },
        "medication_taken": True
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\nStatut: {data.get('success')}")
            
            # Prédiction
            pred = data.get('prediction', {})
            print(f"\nPREDICTION:")
            print(f"  Score: {pred.get('risk_score')}/100")
            print(f"  Niveau: {pred.get('risk_level')}")
            print(f"  Confiance: {pred.get('confidence')}%")
            print(f"  Notification: {pred.get('should_notify')}")
            print(f"  Couleur: {pred.get('risk_color')}")
            print(f"  Icone: {pred.get('risk_icon')}")
            
            # Profil
            profile_ctx = data.get('profile_context', {})
            if profile_ctx:
                print(f"\nPROFIL:")
                print(f"  Nom: {profile_ctx.get('name')}")
                print(f"  Message: {profile_ctx.get('message')}")
                print(f"  Conseil: {profile_ctx.get('specific_advice')}")
            
            # Facteurs
            factors = data.get('factors', [])
            print(f"\nFACTEURS ({len(factors)}):")
            for i, f in enumerate(factors[:3], 1):
                print(f"  {i}. {f.get('factor')}: {f.get('value')} ({f.get('contribution_percent')}%)")
            
            # Recommandations
            recs = data.get('recommendations', {})
            print(f"\nRECOMMANDATIONS:")
            imm = recs.get('immediate', [])
            prev = recs.get('preventive', [])
            env = recs.get('environmental', [])
            print(f"  Immediates: {len(imm)}")
            if imm:
                for r in imm[:2]:
                    print(f"    - {r}")
            print(f"  Preventives: {len(prev)}")
            if prev:
                for r in prev[:2]:
                    print(f"    - {r}")
            print(f"  Environnementales: {len(env)}")
            if env:
                for r in env[:2]:
                    print(f"    - {r}")
            
            # Environnement
            environment = data.get('environment', {})
            if environment:
                weather = environment.get('weather', {})
                air = environment.get('air_quality', {})
                print(f"\nENVIRONNEMENT:")
                print(f"  Temperature: {weather.get('temperature')}C")
                print(f"  AQI: {air.get('aqi')}")
            
            # Capteurs
            sensors = data.get('sensors', {})
            if sensors:
                print(f"\nCAPTEURS:")
                print(f"  SpO2: {sensors.get('spo2')}%")
                print(f"  BPM: {sensors.get('heart_rate')}")
                print(f"  Source: {sensors.get('source')}")
            
        else:
            print(f"\nErreur {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("\nAPI non demarree. Demarrez avec: python api/app.py")
        break
    except Exception as e:
        print(f"\nErreur: {e}")

print("\n" + "=" * 80)
