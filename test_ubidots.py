import requests
import json

UBIDOTS_TOKEN = "BBUS-IW4Xne31AviZZ0jAAojvf3FczCx8Vw"

print("=" * 60)
print("TEST CONNEXION UBIDOTS")
print("=" * 60)

# Test 1: Lister tous les devices
print("\n1. Liste de tous vos devices:")
print("-" * 60)
headers = {'X-Auth-Token': UBIDOTS_TOKEN, 'Content-Type': 'application/json'}

try:
    url = "https://industrial.api.ubidots.com/api/v1.6/devices/"
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        devices = response.json()
        if isinstance(devices, dict) and 'results' in devices:
            devices = devices['results']
        
        print(f"✓ Nombre de devices: {len(devices)}")
        for device in devices:
            print(f"\n  Device: {device.get('label', 'N/A')}")
            print(f"  Nom: {device.get('name', 'N/A')}")
            print(f"  ID: {device.get('id', 'N/A')}")
            print(f"  Variables: {device.get('variables_number', 0)}")
    else:
        print(f"✗ Erreur {response.status_code}: {response.text}")
except Exception as e:
    print(f"✗ Erreur de connexion: {e}")

# Test 2: Vérifier le device "bracelet"
print("\n\n2. Détails du device 'bracelet':")
print("-" * 60)
try:
    url = "https://industrial.api.ubidots.com/api/v1.6/devices/bracelet/"
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        device = response.json()
        print(f"✓ Device trouvé: {device.get('name', 'N/A')}")
        print(f"  ID: {device.get('id', 'N/A')}")
        print(f"  Dernière activité: {device.get('last_activity', 'N/A')}")
        
        # Lister les variables
        print("\n  Variables disponibles:")
        for key, value in device.items():
            if isinstance(value, dict) and 'last_value' in value:
                last_val = value.get('last_value', {})
                print(f"    - {key}: {last_val.get('value', 'N/A')} (timestamp: {last_val.get('timestamp', 'N/A')})")
        
        print("\n  Structure complète:")
        print(json.dumps(device, indent=2))
    else:
        print(f"✗ Device 'bracelet' non trouvé (erreur {response.status_code})")
        print(f"  Réponse: {response.text}")
except Exception as e:
    print(f"✗ Erreur: {e}")

# Test 3: Vérifier les variables du device par ID
print("\n\n3. Variables par ID de device:")
print("-" * 60)
DEVICE_ID = "696c16da6b8f94fd52f77962"  # ID du device bracelet
try:
    url = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_ID}/"
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        device = response.json()
        print(f"✓ Device ID {DEVICE_ID} trouvé")
        print(f"  Label: {device.get('label', 'N/A')}")
        
        # Variables avec leurs dernières valeurs
        print("\n  Dernières valeurs:")
        for key, value in device.items():
            if isinstance(value, dict) and 'last_value' in value:
                last_val = value.get('last_value', {})
                if last_val:
                    from datetime import datetime
                    ts = last_val.get('timestamp', 0)
                    if ts:
                        dt = datetime.fromtimestamp(ts / 1000)
                        print(f"    {key}: {last_val.get('value', 'N/A')} ({dt.strftime('%Y-%m-%d %H:%M:%S')})")
    else:
        print(f"✗ Erreur {response.status_code}")
except Exception as e:
    print(f"✗ Erreur: {e}")

print("\n" + "=" * 60)
print("FIN DU TEST")
print("=" * 60)
