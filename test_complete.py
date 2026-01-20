import requests
from datetime import datetime
import json

UBIDOTS_TOKEN = "BBUS-IW4Xne31AviZZ0jAAojvf3FczCx8Vw"
DEVICE_ID = "696c16da6b8f94fd52f77962"

print("=" * 70)
print("TEST COMPLET UBIDOTS - TOUTES LES MÉTHODES")
print("=" * 70)

headers = {'X-Auth-Token': UBIDOTS_TOKEN, 'Content-Type': 'application/json'}

# Test 1: Lister tous les datasources
print("\n[Test 1: Liste de tous les datasources]")
urls_to_try = [
    "https://industrial.api.ubidots.com/api/v2.0/datasources/",
    "https://industrial.api.ubidots.com/api/v1.6/datasources/"
]

for url in urls_to_try:
    try:
        print(f"  Essai: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                results = data.get('results', data.get('datasources', []))
            else:
                results = data
            
            print(f"  ✓ {len(results)} datasources trouvés")
            for ds in results[:3]:  # Afficher les 3 premiers
                print(f"    - {ds.get('label', 'N/A')} (ID: {ds.get('id', 'N/A')})")
            break
        else:
            print(f"  ✗ Status {response.status_code}")
    except Exception as e:
        print(f"  ✗ Erreur: {e}")

# Test 2: Accès direct par ID
print(f"\n[Test 2: Accès datasource par ID: {DEVICE_ID}]")
urls_to_try = [
    f"https://industrial.api.ubidots.com/api/v2.0/datasources/{DEVICE_ID}/",
    f"https://industrial.api.ubidots.com/api/v1.6/datasources/{DEVICE_ID}/"
]

datasource_found = False
for url in urls_to_try:
    try:
        print(f"  Essai: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Datasource trouvé: {data.get('name', 'N/A')}")
            print(f"    Variables: {data.get('number_of_variables', data.get('variables_number', 0))}")
            datasource_found = True
            
            # Structure complète
            print("\n  Structure complète:")
            print(json.dumps(data, indent=2)[:1000] + "...")
            break
        else:
            print(f"  ✗ Status {response.status_code}")
    except Exception as e:
        print(f"  ✗ Erreur: {e}")

# Test 3: Variables du datasource
print(f"\n[Test 3: Variables du datasource {DEVICE_ID}]")
urls_to_try = [
    f"https://industrial.api.ubidots.com/api/v2.0/datasources/{DEVICE_ID}/variables/",
    f"https://industrial.api.ubidots.com/api/v1.6/datasources/{DEVICE_ID}/variables/"
]

for url in urls_to_try:
    try:
        print(f"  Essai: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            variables = data.get('results', data) if isinstance(data, dict) else data
            
            print(f"  ✓ {len(variables)} variables trouvées\n")
            
            for var in variables:
                label = var.get('label', 'N/A')
                var_id = var.get('id')
                
                # Récupérer la dernière valeur
                val_url = f"https://industrial.api.ubidots.com/api/v1.6/variables/{var_id}/values/?page_size=1"
                val_response = requests.get(val_url, headers=headers, timeout=10)
                
                if val_response.status_code == 200:
                    values = val_response.json()
                    results = values.get('results', values) if isinstance(values, dict) else values
                    
                    if results and len(results) > 0:
                        last_value = results[0]
                        value = last_value.get('value', 'N/A')
                        timestamp = last_value.get('timestamp', 0)
                        
                        dt = datetime.fromtimestamp(timestamp / 1000) if timestamp else None
                        time_str = dt.strftime('%Y-%m-%d %H:%M:%S') if dt else 'N/A'
                        
                        print(f"    ✓ {label:15} = {value:8.2f}  ({time_str})")
                    else:
                        print(f"    ✗ {label:15} = PAS DE VALEURS")
                else:
                    print(f"    ✗ {label:15} = Erreur {val_response.status_code}")
            break
        else:
            print(f"  ✗ Status {response.status_code}")
    except Exception as e:
        print(f"  ✗ Erreur: {e}")

print("\n" + "=" * 70)
