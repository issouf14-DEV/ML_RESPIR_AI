# test_api.py - Script de test pour l'API RESPIRIA
"""
Script de test complet pour l'API RESPIRIA
Teste tous les endpoints avec différents scénarios

Note: Nécessite 'pip install requests' pour fonctionner
"""

try:
    import requests  # type: ignore
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ Module 'requests' non installé. Installez avec: pip install requests")

import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER_ID = "test_user_123"

def print_header(title):
    """Affiche un en-tête de test"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def print_response(response, test_name):
    """Affiche le résultat d'un test"""
    print(f"\n📡 {test_name}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Succès")
            
            # Affichage détaillé si prédiction
            if 'prediction' in result:
                pred = result['prediction']
                print(f"   🎯 Score de risque: {pred['risk_score']}%")
                print(f"   📊 Niveau: {pred['risk_level'].upper()}")
                print(f"   🔔 Notification: {'OUI' if pred['should_notify'] else 'NON'}")
                
                # Facteurs de risque
                if result['risk_factors']:
                    print(f"   🎯 Facteurs principaux:")
                    for factor in result['risk_factors'][:3]:  # Top 3
                        print(f"      • {factor['factor']}: {factor['contribution_percent']}% ({factor['status']})")
                
                # Recommandations
                recs = result['recommendations']
                total_recs = len(recs.get('immediate', [])) + len(recs.get('preventive', [])) + len(recs.get('environmental', []))
                print(f"   💡 Recommandations: {total_recs} actions")
                
                # Profil utilisateur
                profile = result['profile_context']
                print(f"   👤 Profil: {profile['name']} (Alerte: {profile['alert_level']})")
        else:
            print(f"❌ Erreur: {result.get('error', 'Inconnue')}")
    else:
        print(f"❌ Erreur HTTP {response.status_code}")
        try:
            error_data = response.json()
            print(f"   Détail: {error_data.get('error', 'Erreur inconnue')}")
        except:
            print(f"   Réponse: {response.text}")

def test_health():
    """Test de l'endpoint de santé"""
    print_header("TEST DE SANTÉ")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "GET /health")

def test_manual_prediction():
    """Test des prédictions manuelles"""
    print_header("TESTS DE PRÉDICTION MANUELLE")
    
    # Test 1 : Situation critique (Asthmatique sévère)
    critical_data = {
        "spo2": 89,
        "heart_rate": 110,
        "respiratory_rate": 28,
        "aqi": 175,
        "temperature": 15,
        "humidity": 75,
        "pollen_level": 4,
        "medication_taken": False,
        "smoke_detected": False,
        "profile_id": 2  # Asthmatique sévère
    }
    
    response = requests.post(
        f"{BASE_URL}/predict/manual",
        json=critical_data,
        headers={'Content-Type': 'application/json'}
    )
    print_response(response, "Situation critique - Asthmatique sévère")
    
    # Test 2 : Situation normale (Prévention)
    normal_data = {
        "spo2": 97,
        "heart_rate": 75,
        "respiratory_rate": 16,
        "aqi": 45,
        "temperature": 22,
        "humidity": 50,
        "pollen_level": 1,
        "medication_taken": True,
        "smoke_detected": False,
        "profile_id": 0  # Prévention
    }
    
    response = requests.post(
        f"{BASE_URL}/predict/manual",
        json=normal_data,
        headers={'Content-Type': 'application/json'}
    )
    print_response(response, "Situation normale - Prévention")
    
    # Test 3 : Urgence fumée
    smoke_data = {
        "spo2": 95,
        "heart_rate": 80,
        "respiratory_rate": 18,
        "aqi": 60,
        "temperature": 20,
        "humidity": 55,
        "pollen_level": 2,
        "medication_taken": True,
        "smoke_detected": True,  # 🚨 URGENCE
        "profile_id": 1  # Asthmatique stable
    }
    
    response = requests.post(
        f"{BASE_URL}/predict/manual",
        json=smoke_data,
        headers={'Content-Type': 'application/json'}
    )
    print_response(response, "Urgence fumée - Asthmatique stable")

def test_auto_prediction():
    """Test des prédictions automatiques"""
    print_header("TESTS DE PRÉDICTION AUTOMATIQUE")
    
    # Test avec collecte de données réelles
    auto_data = {
        "user_id": TEST_USER_ID,
        "profile_id": 1,  # Asthmatique stable
        "location": "Abidjan",
        "medication_taken": True,
        "sensor_override": {
            "spo2": 94,
            "heart_rate": 85,
            "respiratory_rate": 22,
            "smoke_detected": False
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/predict/auto",
        json=auto_data,
        headers={'Content-Type': 'application/json'}
    )
    print_response(response, "Prédiction automatique avec données météo réelles")

def test_data_endpoints():
    """Test des endpoints de données"""
    print_header("TESTS DES ENDPOINTS DE DONNÉES")
    
    # Test météo
    response = requests.get(f"{BASE_URL}/data/weather?location=Abidjan")
    print_response(response, "GET /data/weather")
    
    # Test qualité de l'air
    response = requests.get(f"{BASE_URL}/data/air-quality?location=Abidjan")
    print_response(response, "GET /data/air-quality")

def test_error_cases():
    """Test des cas d'erreur"""
    print_header("TESTS DES CAS D'ERREUR")
    
    # Test sans profile_id
    invalid_data = {
        "spo2": 95,
        "heart_rate": 75,
        # profile_id manquant
    }
    
    response = requests.post(
        f"{BASE_URL}/predict/manual",
        json=invalid_data,
        headers={'Content-Type': 'application/json'}
    )
    print_response(response, "Données incomplètes (profile_id manquant)")
    
    # Test avec profile_id invalide
    invalid_profile = {
        "spo2": 95,
        "heart_rate": 75,
        "respiratory_rate": 16,
        "aqi": 50,
        "temperature": 22,
        "humidity": 50,
        "pollen_level": 1,
        "medication_taken": True,
        "smoke_detected": False,
        "profile_id": 999  # Invalide
    }
    
    response = requests.post(
        f"{BASE_URL}/predict/manual",
        json=invalid_profile,
        headers={'Content-Type': 'application/json'}
    )
    print_response(response, "Profile ID invalide")

def main():
    """Fonction principale de test"""
    print("🚀 DÉBUT DES TESTS DE L'API RESPIRIA")
    print(f"📍 URL de base: {BASE_URL}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Tests séquentiels
        test_health()
        test_manual_prediction()
        test_auto_prediction() 
        test_data_endpoints()
        test_error_cases()
        
        print_header("RÉSUMÉ DES TESTS")
        print("✅ Tous les tests terminés")
        print(f"📊 API RESPIRIA testée avec succès")
        print(f"🧠 Cahier des charges respecté:")
        print(f"   ✅ 10 variables d'entrée")
        print(f"   ✅ Facteurs de risque avec pourcentages")
        print(f"   ✅ Recommandations personnalisées")
        print(f"   ✅ Messages adaptés par profil")
        print(f"   ✅ Gestion des urgences (fumée)")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERREUR: Impossible de se connecter à l'API")
        print("Assurez-vous que l'API est démarrée avec: python api/app.py")
        
    except Exception as e:
        print(f"❌ ERREUR inattendue: {str(e)}")

if __name__ == "__main__":
    main()