"""
Test RESPIRIA avec données Ubidots en temps réel
"""
import requests
import json
import urllib3

# Désactiver avertissements SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print('='*60)
print('TEST COMPLET AVEC DONNEES REELLES UBIDOTS')
print('='*60)

# Configuration Ubidots
UBIDOTS_TOKEN = 'BBUS-IW4Xne31AviZZ0jAAojvf3FczCx8Vw'
DEVICE_LABEL = 'bracelet'
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
    r = requests.post('https://ml-respir-ai.onrender.com/predict/auto', json=payload, timeout=60, verify=False)
    result = r.json()
    print(f'  Status: {r.status_code}')
    print(f'  Risk Level: {result.get("prediction", {}).get("risk_level")}')
    print(f'  Risk Score: {result.get("prediction", {}).get("risk_score")}')
    print(f'  Confidence: {result.get("prediction", {}).get("confidence")}')
    print(f'  Message: {result.get("profile_context", {}).get("message")}')
except Exception as e:
    print(f'  Erreur: {e}')

# 3. Test endpoint /predict (base)
print('\n🔮 TEST PREDICTION /predict...')
base_payload = {
    'spo2': sensors['spo2'] if sensors['spo2'] > 0 else 96,
    'heart_rate': sensors['bpm'] if sensors['bpm'] > 0 else 75,
    'temperature': sensors['temperature'],
    'humidity': sensors['humidity'],
    'co2_level': sensors['eco2'],
    'pm25': 15,
    'pollen_level': 3.5,
    'location': 'Abidjan',
    'medication_taken': True,
    'respiratory_rate': 16
}

try:
    r = requests.post('https://ml-respir-ai.onrender.com/predict', json=base_payload, timeout=60, verify=False)
    result = r.json()
    print(f'  Status: {r.status_code}')
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f'  Erreur: {e}')

# 4. Test health
print('\n❤️ HEALTH CHECK...')
try:
    r = requests.get('https://ml-respir-ai.onrender.com/health', timeout=30, verify=False)
    print(f'  Status: {r.status_code}')
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f'  Erreur: {e}')

print('\n' + '='*60)
print('TEST TERMINE')
print('='*60)
