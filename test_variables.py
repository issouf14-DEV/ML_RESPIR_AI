import requests
from datetime import datetime

UBIDOTS_TOKEN = "BBUS-IW4Xne31AviZZ0jAAojvf3FczCx8Vw"
DEVICE_LABEL = "bracelet"

print("=" * 60)
print("LECTURE DES VARIABLES UBIDOTS - DEVICE BRACELET")
print("=" * 60)

headers = {'X-Auth-Token': UBIDOTS_TOKEN, 'Content-Type': 'application/json'}

# Récupérer les variables du device
url = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/variables/"
print(f"\nURL: {url}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        
        if isinstance(data, dict) and 'results' in data:
            variables = data['results']
        else:
            variables = data if isinstance(data, list) else []
        
        print(f"✓ {len(variables)} variables trouvées\n")
        
        for var in variables:
            label = var.get('label', 'N/A')
            name = var.get('name', 'N/A')
            last_value = var.get('last_value', {})
            
            if last_value:
                value = last_value.get('value', 'N/A')
                timestamp = last_value.get('timestamp', 0)
                
                if timestamp:
                    dt = datetime.fromtimestamp(timestamp / 1000)
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    time_str = 'N/A'
                
                print(f"Variable: {label}")
                print(f"  Nom: {name}")
                print(f"  Valeur: {value}")
                print(f"  Date: {time_str}")
                print()
            else:
                print(f"Variable: {label} - PAS DE DONNÉES")
                print()
    else:
        print(f"✗ Erreur {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"✗ Erreur: {e}")

print("=" * 60)
