import requests
from datetime import datetime

UBIDOTS_TOKEN = "BBUS-IW4Xne31AviZZ0jAAojvf3FczCx8Vw"
DEVICE_ID = "696c16da6b8f94fd52f77962"

print("=" * 60)
print("TEST API UBIDOTS v2.0")
print("=" * 60)

headers = {'X-Auth-Token': UBIDOTS_TOKEN, 'Content-Type': 'application/json'}

# Test avec l'API v2.0
url = f"https://industrial.api.ubidots.com/api/v2.0/devices/{DEVICE_ID}/"
print(f"\nURL: {url}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}\n")
    
    if response.status_code == 200:
        device = response.json()
        
        print(f"✓ Device: {device.get('name', 'N/A')}")
        print(f"  Variables: {device.get('properties', {}).get('_numberVariables', 0)}")
        
        # Récupérer les variables
        variables_url = f"https://industrial.api.ubidots.com/api/v2.0/devices/{DEVICE_ID}/variables/"
        print(f"\nRécupération des variables...")
        
        var_response = requests.get(variables_url, headers=headers, timeout=10)
        
        if var_response.status_code == 200:
            variables = var_response.json().get('results', [])
            print(f"✓ {len(variables)} variables trouvées\n")
            
            for var in variables:
                label = var.get('label', 'N/A')
                name = var.get('name', 'N/A')
                
                # Récupérer la dernière valeur
                var_id = var.get('id')
                value_url = f"https://industrial.api.ubidots.com/api/v2.0/variables/{var_id}/values/"
                value_response = requests.get(value_url, headers=headers, params={'page_size': 1}, timeout=10)
                
                if value_response.status_code == 200:
                    values = value_response.json().get('results', [])
                    if values:
                        last_value = values[0]
                        value = last_value.get('value', 'N/A')
                        timestamp = last_value.get('timestamp', 0)
                        
                        dt = datetime.fromtimestamp(timestamp / 1000) if timestamp else None
                        time_str = dt.strftime('%Y-%m-%d %H:%M:%S') if dt else 'N/A'
                        
                        print(f"✓ {label}: {value} ({time_str})")
                    else:
                        print(f"✗ {label}: PAS DE DONNÉES")
                else:
                    print(f"✗ {label}: Erreur {value_response.status_code}")
        else:
            print(f"✗ Erreur variables: {var_response.status_code}")
            print(var_response.text)
    else:
        print(f"✗ Erreur {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"✗ Erreur: {e}")

print("\n" + "=" * 60)
