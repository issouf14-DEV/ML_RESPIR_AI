# test_backend_integration.py - Test complet avec authentification
"""
Test complet du système RESPIRIA avec les vraies APIs Backend
Inclut authentification, collecte de données, et prédictions IA

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
from api.respiria_ai_predictor import RespiriaAIPredictor

# Configuration
BACKEND_URL = "https://respira-backend.onrender.com/api/v1"
AI_API_URL = "http://localhost:5000"

class RespiriaBackendTester:
    """Testeur complet pour les APIs RESPIRIA Backend + IA"""
    
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.ai_api_url = AI_API_URL
        self.access_token = None
        self.refresh_token = None
        
        # Initialiser le prédicteur IA local
        self.ai_predictor = RespiriaAIPredictor()
        
    def authenticate(self, email: str, password: str) -> bool:
        """Authentification avec le backend"""
        try:
            print("🔐 Authentification avec le backend...")
            
            response = requests.post(
                f"{self.backend_url}/users/auth/login/",
                json={"email": email, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens['access']
                self.refresh_token = tokens['refresh']
                print("✅ Authentification réussie")
                return True
            else:
                print(f"❌ Échec authentification: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur authentification: {e}")
            return False
    
    def create_test_account(self) -> bool:
        """Créer un compte de test si nécessaire"""
        test_data = {
            "email": "test.respiria@example.com",
            "username": "test_respiria",
            "password": "TestRespiriaAI123!",
            "password_confirm": "TestRespiriaAI123!",
            "profile_type": "ASTHMATIC",
            "first_name": "Test",
            "last_name": "Respiria"
        }
        
        try:
            print("👤 Création d'un compte de test...")
            
            response = requests.post(
                f"{self.backend_url}/users/auth/register/",
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                self.access_token = result['tokens']['access']
                self.refresh_token = result['tokens']['refresh']
                print("✅ Compte de test créé avec succès")
                return True
            elif response.status_code == 400:
                print("ℹ️ Compte existe déjà, tentative de connexion...")
                return self.authenticate(test_data['email'], test_data['password'])
            else:
                print(f"❌ Échec création compte: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur création compte: {e}")
            return False
    
    def test_weather_api(self, location="Abidjan"):
        """Test de l'API météo avec authentification"""
        print(f"\n🌤️ Test API Météo - {location}")
        print("-" * 40)
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(
                f"{self.backend_url}/environment/weather/?city={location}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Succès API Météo")
                print(f"   🌡️ Température: {data.get('temperature', 'N/A')}°C")
                print(f"   💧 Humidité: {data.get('humidity', 'N/A')}%")
                print(f"   🌍 Ville: {data.get('city', 'N/A')}")
                print(f"   🌤️ Condition: {data.get('description', 'N/A')}")
                return data
            else:
                print(f"❌ Erreur API Météo: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Exception API Météo: {e}")
            return None
    
    def test_air_quality_api(self, location="Abidjan"):
        """Test de l'API qualité de l'air avec authentification"""
        print(f"\n🌫️ Test API Qualité Air - {location}")
        print("-" * 40)
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(
                f"{self.backend_url}/environment/air-quality/?city={location}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Succès API Qualité Air")
                print(f"   🌫️ AQI: {data.get('aqi', 'N/A')}")
                print(f"   📈 Niveau: {data.get('quality_level', 'N/A')}")
                print(f"   🏭 Polluant principal: {data.get('main_pollutant', 'N/A')}")
                
                pollutants = data.get('pollutants', {})
                print(f"   🔬 PM2.5: {pollutants.get('pm25', 'N/A')} µg/m³")
                print(f"   🔬 PM10: {pollutants.get('pm10', 'N/A')} µg/m³")
                return data
            else:
                print(f"❌ Erreur API Qualité Air: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Exception API Qualité Air: {e}")
            return None
    
    def test_sensors_api(self):
        """Test de l'API capteurs avec authentification"""
        print(f"\n🔌 Test API Capteurs Ubidots")
        print("-" * 40)
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            
            # Test capteurs MAX30102 (médical)
            response = requests.get(
                f"{self.backend_url}/sensors/data/max30102/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Succès API Capteurs")
                print(f"   🫁 SpO2: {data.get('spo2', 'N/A')}%")
                print(f"   ❤️ Fréquence cardiaque: {data.get('heart_rate', 'N/A')} bpm")
                print(f"   📊 Timestamp: {data.get('timestamp', 'N/A')}")
                return data
            else:
                print(f"❌ Erreur API Capteurs: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Exception API Capteurs: {e}")
            return None
    
    def test_ai_prediction_with_real_data(self):
        """Test de prédiction IA avec vraies données du backend"""
        print(f"\n🧠 Test Prédiction IA avec Vraies Données")
        print("=" * 50)
        
        # Collecter les vraies données
        weather = self.test_weather_api()
        air_quality = self.test_air_quality_api()
        sensors = self.test_sensors_api()
        
        # Construire les données pour l'IA
        prediction_data = {
            # Données physiologiques (capteurs ou par défaut)
            'spo2': sensors.get('spo2', 94.0) if sensors else 94.0,
            'heart_rate': sensors.get('heart_rate', 85.0) if sensors else 85.0,
            'respiratory_rate': 18.0,  # À calculer ou recevoir des capteurs
            
            # Données environnementales (APIs)
            'aqi': air_quality.get('aqi', 60) if air_quality else 60,
            'temperature': weather.get('temperature', 28.0) if weather else 28.0,
            'humidity': weather.get('humidity', 70.0) if weather else 70.0,
            
            # Estimation pollen basée sur AQI
            'pollen_level': self._estimate_pollen(air_quality.get('aqi', 60) if air_quality else 60),
            
            # Paramètres utilisateur
            'medication_taken': False,  # Test sans médicament
            'smoke_detected': False,    # Pas de fumée
            'profile_id': 1             # Asthmatique stable
        }
        
        print(f"\n📊 DONNÉES POUR PRÉDICTION IA:")
        for key, value in prediction_data.items():
            print(f"   • {key}: {value}")
        
        # Faire la prédiction
        print(f"\n🤖 Exécution de la prédiction...")
        result = self.ai_predictor.predict(prediction_data)
        
        if result.get('success'):
            self._display_ai_results(result)
        else:
            print(f"❌ Erreur prédiction: {result.get('error')}")
        
        return result
    
    def _estimate_pollen(self, aqi):
        """Estime le pollen basé sur l'AQI"""
        if aqi <= 50:
            return 1
        elif aqi <= 100:
            return 2
        elif aqi <= 150:
            return 3
        elif aqi <= 200:
            return 4
        else:
            return 5
    
    def _display_ai_results(self, result):
        """Affiche les résultats IA de manière claire"""
        pred = result['prediction']
        
        print(f"\n🎯 RÉSULTATS DE PRÉDICTION IA:")
        print(f"   📈 Score de risque: {pred['risk_score']}%")
        print(f"   🚨 Niveau: {pred['risk_level'].upper()}")
        print(f"   📊 Confiance: {pred['confidence']*100:.1f}%")
        print(f"   🔔 Notification: {'OUI' if pred['should_notify'] else 'NON'}")
        
        # Facteurs de risque
        print(f"\n🎯 FACTEURS DE RISQUE:")
        for factor in result['risk_factors']:
            print(f"   • {factor['factor']}: {factor['contribution_percent']}% ({factor['status']})")
            print(f"     → {factor['message']}")
        
        # Recommandations
        recs = result['recommendations']
        if recs['immediate']:
            print(f"\n🚨 ACTIONS IMMÉDIATES:")
            for action in recs['immediate']:
                print(f"   • {action}")
        
        if recs['preventive']:
            print(f"\n🛡️ ACTIONS PRÉVENTIVES:")
            for action in recs['preventive']:
                print(f"   • {action}")
        
        if recs['environmental']:
            print(f"\n🌍 CONSEILS ENVIRONNEMENTAUX:")
            for action in recs['environmental']:
                print(f"   • {action}")
        
        # Profil utilisateur
        profile = result['profile_context']
        print(f"\n👤 PROFIL UTILISATEUR:")
        print(f"   • Type: {profile['name']}")
        print(f"   • Message: {profile['message']}")
    
    def run_complete_test(self):
        """Test complet du système RESPIRIA"""
        print("🚀 DÉBUT DU TEST COMPLET RESPIRIA")
        print("=" * 60)
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print(f"🔗 Backend: {self.backend_url}")
        
        # Étape 1: Authentification ou création compte
        if not self.create_test_account():
            print("❌ Impossible de s'authentifier - Test arrêté")
            return False
        
        # Étape 2: Test des APIs individuelles
        print(f"\n📡 PHASE 2: TEST DES APIs BACKEND")
        weather_ok = self.test_weather_api() is not None
        air_ok = self.test_air_quality_api() is not None
        sensors_ok = self.test_sensors_api() is not None
        
        # Étape 3: Test prédiction IA avec vraies données
        print(f"\n🧠 PHASE 3: TEST PRÉDICTION IA")
        ai_result = self.test_ai_prediction_with_real_data()
        ai_ok = ai_result and ai_result.get('success', False)
        
        # Résumé
        print(f"\n📊 RÉSUMÉ DU TEST COMPLET:")
        print(f"   🔐 Authentification: ✅ Réussie")
        print(f"   🌤️ API Météo: {'✅ OK' if weather_ok else '❌ Échec'}")
        print(f"   🌫️ API Qualité Air: {'✅ OK' if air_ok else '❌ Échec'}")
        print(f"   🔌 API Capteurs: {'✅ OK' if sensors_ok else '❌ Échec'}")
        print(f"   🧠 IA Prédiction: {'✅ OK' if ai_ok else '❌ Échec'}")
        
        success_count = sum([True, weather_ok, air_ok, sensors_ok, ai_ok])
        print(f"\n🎯 SCORE GLOBAL: {success_count}/5 ({success_count*20}%)")
        
        if success_count >= 4:
            print("🎉 SYSTÈME RESPIRIA OPÉRATIONNEL!")
        else:
            print("⚠️ Système partiellement opérationnel")
        
        return success_count >= 4

def main():
    """Fonction principale de test"""
    tester = RespiriaBackendTester()
    
    print("🧪 TESTEUR COMPLET RESPIRIA - Backend + IA")
    print("=" * 60)
    
    # Lancer le test complet
    success = tester.run_complete_test()
    
    if success:
        print("\n✅ SYSTÈME PRÊT POUR PRODUCTION!")
        print("🚀 Tu peux maintenant intégrer dans Flutter")
    else:
        print("\n⚠️ Quelques APIs nécessitent des ajustements")
        print("🔧 Contacte ton dev backend pour résoudre les problèmes")

if __name__ == "__main__":
    main()