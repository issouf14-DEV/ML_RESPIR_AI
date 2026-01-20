import requests
from datetime import datetime

UBIDOTS_TOKEN = "BBUS-IW4Xne31AviZZ0jAAojvf3FczCx8Vw"
DEVICE_LABEL = "bracelet"

print("=" * 70)
print("LECTURE DONNEES UBIDOTS - DATASOURCE API")
print("=" * 70)

headers = {'X-Auth-Token': UBIDOTS_TOKEN, 'Content-Type': 'application/json'}

# Méthode 1: Via datasources (ancien endpoint)
print("\n[Méthode 1: API Datasources]")
url = f"https://industrial.api.ubidots.com/api/v1.6/datasources/{DEVICE_LABEL}/"
print(f"URL: {url}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Datasource: {data.get('name', 'N/A')}")
        print(f"  Variables: {data.get('number_of_variables', 0)}")
        
        # Récupérer les variables
        vars_url = f"https://industrial.api.ubidots.com/api/v1.6/datasources/{DEVICE_LABEL}/variables/"
        vars_response = requests.get(vars_url, headers=headers, timeout=10)
        
        if vars_response.status_code == 200:
            variables = vars_response.json()
            if isinstance(variables, dict) and 'results' in variables:
                variables = variables['results']
            
            print(f"\n  Variables trouvées: {len(variables)}")
            print("-" * 70)
            
            for var in variables:
                label = var.get('label', 'N/A')
                name = var.get('name', 'N/A')
                
                # Récupérer la dernière valeur
                var_id = var.get('id')
                val_url = f"https://industrial.api.ubidots.com/api/v1.6/variables/{var_id}/values/"
                val_response = requests.get(val_url, headers=headers, params={'page_size': 1}, timeout=10)
                
                if val_response.status_code == 200:
                    values = val_response.json()
                    if isinstance(values, dict) and 'results' in values:
                        values = values['results']
                    
                    if values and len(values) > 0:
                        last_value = values[0]
                        value = last_value.get('value', 'N/A')
                        timestamp = last_value.get('timestamp', 0)
                        
                        dt = datetime.fromtimestamp(timestamp / 1000) if timestamp else None
                        time_str = dt.strftime('%H:%M:%S') if dt else 'N/A'
                        
                        # Déterminer la couleur selon le type de capteur
                        status = "OK"
                        if 'spo2' in label.lower():
                            status = "ALERTE" if value < 95 else "OK"
                        elif 'bpm' in label.lower() or 'heart' in label.lower():
                            status = "ALERTE" if value > 100 or value < 60 else "OK"
                        elif 'eco2' in label.lower():
                            status = "ALERTE" if value > 1000 else "OK"
                        elif 'tvoc' in label.lower():
                            status = "ALERTE" if value > 220 else "OK"
                        
                        print(f"  {label:15} = {value:8.1f}  [{status}]  ({time_str})")
                    else:
                        print(f"  {label:15} = PAS DE DONNÉES")
                else:
                    print(f"  {label:15} = Erreur {val_response.status_code}")
        else:
            print(f"\n✗ Erreur récupération variables: {vars_response.status_code}")
    else:
        print(f"✗ Erreur: {response.text}")
        
except Exception as e:
    print(f"✗ Erreur: {e}")

print("\n" + "=" * 70)
