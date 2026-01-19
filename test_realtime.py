"""
Test RESPIRIA avec données Ubidots en temps réel
"""
import requests  # type: ignore
import json
import warnings
import os

# Charger les variables d'environnement
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass

# Désactiver avertissements SSL
warnings.filterwarnings('ignore')

print('='*60)
print('TEST COMPLET AVEC DONNEES REELLES UBIDOTS')
print('='*60)

# Configuration depuis .env
UBIDOTS_TOKEN = os.environ.get('UBIDOTS_TOKEN')
DEVICE_LABEL = os.environ.get('UBIDOTS_DEVICE_LABEL', 'bracelet')
ML_API_URL = os.environ.get('ML_API_URL', 'https://ml-respir-ai.onrender.com')

if not UBIDOTS_TOKEN:
    print("⚠️ UBIDOTS_TOKEN non défini dans .env")
    exit(1)

headers = {'X-Auth-Token': UBIDOTS_TOKEN}

# 1. Récupérer données Ubidots réelles
print('\n📡 RECUPERATION DONNEES UBIDOTS...')
sensors = {}
for var in ['spo2', 'bpm', 'temperature', 'humidity', 'eco2', 'tvoc']:
    try:
        url = f'https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/{var}/lv'
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        sensors[var] = float(r.text) if r.status_code == 200 else 0
        print(f'  {var}: {sensors[var]}')
    except Exception as e:
        sensors[var] = 0
        print(f'  {var}: Erreur - {e}')

# 2. Test prédiction avec données réelles
print('\n🔮 TEST PREDICTION /predict/auto...')
payload = {
    'user_id': 'ubidots_realtime',
    'profile_id': 1,
    'location': 'Abidjan',
    'medication_taken': True,
    'sensor_override': {
        'spo2': sensors['spo2'] if sensors['spo2'] > 0 else 96,
        'heart_rate': sensors['bpm'] if sensors['bpm'] > 0 else 75
    }
}

try:
    r = requests.post(f'{ML_API_URL}/predict/auto', json=payload, timeout=60, verify=False)
    result = r.json()
    print(f'  Status: {r.status_code}')
    print(f'  Risk Level: {result.get("prediction", {}).get("risk_level")}')
    print(f'  Risk Score: {result.get("prediction", {}).get("risk_score")}')
    print(f'  Confidence: {result.get("prediction", {}).get("confidence")}')
    print(f'  Message: {result.get("profile_context", {}).get("message")}')
except Exception as e:
    print(f'  Erreur: {e}')

# 3. Test endpoint /api/v1/predict (v2.0)
print('\n🔮 TEST PREDICTION /api/v1/predict (v2.0)...')
v2_payload = {
    'user_id': 'ubidots_test',
    'profile_id': 1,
    'location': 'Abidjan',
    'medication_taken': True,
    'sensor_data': {
        'spo2': sensors['spo2'] if sensors['spo2'] > 0 else 96,
        'heart_rate': sensors['bpm'] if sensors['bpm'] > 0 else 75
    }
}

try:
    r = requests.post(f'{ML_API_URL}/api/v1/predict', json=v2_payload, timeout=60, verify=False)
    result = r.json()
    print(f'  Status: {r.status_code}')
    print(f'  Risk Level: {result.get("prediction", {}).get("risk_level")}')
    print(f'  Risk Score: {result.get("prediction", {}).get("risk_score")}')
    print(f'  Message: {result.get("message", {}).get("title")}')
except Exception as e:
    print(f'  Erreur: {e}')

# 4. Test health
print('\n❤️ HEALTH CHECK...')
try:
    r = requests.get(f'{ML_API_URL}/health', timeout=30, verify=False)
    print(f'  Status: {r.status_code}')
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f'  Erreur: {e}')

print('\n' + '='*60)
print('TEST TERMINE')
print('='*60)
