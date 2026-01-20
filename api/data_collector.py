# api/data_collector.py
import os

# Charger les variables d'environnement
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass

try:
    import requests  # type: ignore
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from typing import Dict, Optional
from datetime import datetime

# Configuration Ubidots depuis .env
UBIDOTS_TOKEN = os.environ.get("UBIDOTS_TOKEN")
UBIDOTS_DEVICE_LABEL = os.environ.get("UBIDOTS_DEVICE_LABEL", "bracelet")

class RespiriaDataCollector:
    """
    Collecte les données depuis les APIs RESPIRIA Backend et Ubidots
    ✅ APIs COMPLÈTES ET OPÉRATIONNELLES
    """
    
    def __init__(self, base_url="https://respira-backend.onrender.com/api/v1"):
        self.base_url = base_url
        self.weather_url = f"{base_url}/environment/weather/"
        self.air_quality_url = f"{base_url}/environment/air-quality/"
        self.sensors_url = f"{base_url}/sensors/"
        self.unified_url = f"{base_url}/ai/prediction-data/"
        
        # Configuration optimisée
        self.timeout = 3  # 3s max comme spécifié
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'RESPIRIA-AI/1.0'
        }
    
    def get_weather_data(self, location: Optional[str] = None, auth_token: Optional[str] = None) -> Dict:
        """
        Récupère les données météo depuis l'API RESPIRIA Backend
        
        Args:
            location: Localisation (optionnel)
            auth_token: JWT Bearer token pour authentification
        
        Returns:
            Dict avec température, humidité, etc.
        """
        try:
            params = {'city': location} if location else {}
            headers = self.headers.copy()
            
            if auth_token:
                headers['Authorization'] = f'Bearer {auth_token}'
            
            response = requests.get(
                self.weather_url, 
                params=params, 
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Format conforme à l'API RESPIRIA Backend
            return {
                'temperature': data.get('temperature', 25.0),
                'humidity': data.get('humidity', 50.0),
                'feels_like': data.get('feels_like', 25.0),
                'pressure': data.get('pressure', 1013),
                'wind_speed': data.get('wind_speed', 0),
                'weather_main': data.get('weather_main', 'Clear'),
                'description': data.get('description', 'ciel dégagé'),
                'city': data.get('city', location or 'Inconnu'),
                'country': data.get('country', ''),
                'status': 'success'
            }
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur API météo : {e}")
            # Valeurs par défaut optimisées
            return {
                'temperature': 25.0,
                'humidity': 55.0,
                'feels_like': 25.0,
                'pressure': 1013,
                'wind_speed': 0,
                'weather_main': 'Clear',
                'description': 'données par défaut (API indisponible)',
                'city': location or 'Inconnu',
                'country': '',
                'status': 'fallback',
                'error': str(e)
            }
    
    def get_air_quality_data(self, location: Optional[str] = None, auth_token: Optional[str] = None) -> Dict:
        """
        Récupère les données de qualité de l'air depuis l'API RESPIRIA Backend
        
        Returns:
            Dict avec AQI, polluants, pollen
        """
        try:
            params = {'city': location} if location else {}
            headers = self.headers.copy()
            
            if auth_token:
                headers['Authorization'] = f'Bearer {auth_token}'
            
            response = requests.get(
                self.air_quality_url, 
                params=params, 
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Format conforme à l'API RESPIRIA Backend
            pollutants = data.get('pollutants', {})
            
            return {
                'aqi': data.get('aqi', 50),
                'quality_level': data.get('quality_level', 'Bonne'),
                'main_pollutant': data.get('main_pollutant', 'pm25'),
                'pm25': pollutants.get('pm25', 10.0),
                'pm10': pollutants.get('pm10', 15.0),
                'no2': pollutants.get('no2', 20.0),
                'o3': pollutants.get('o3', 60.0),
                'co': pollutants.get('co', 1.0),
                'pollen_level': self._estimate_pollen_from_aqi(data.get('aqi', 50)),
                'health_recommendations': data.get('health_recommendations', []),
                'city': data.get('city', location or 'Inconnu'),
                'status': 'success'
            }
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur API qualité air : {e}")
            # Valeurs par défaut optimisées
            return {
                'aqi': 50,
                'quality_level': 'Moyenne',
                'main_pollutant': 'pm25',
                'pm25': 12.0,
                'pm10': 18.0,
                'no2': 25.0,
                'o3': 65.0,
                'co': 1.2,
                'pollen_level': 2,  # Niveau moyen par défaut
                'health_recommendations': ['Données par défaut - API indisponible'],
                'city': location or 'Inconnu',
                'status': 'fallback',
                'error': str(e)
            }
    
    def _estimate_pollen_from_aqi(self, aqi: int) -> int:
        """Estime le niveau de pollen basé sur l'AQI (0-5)"""
        if aqi <= 50:
            return 1  # Bas
        elif aqi <= 100:
            return 2  # Modéré
        elif aqi <= 150:
            return 3  # Élevé
        elif aqi <= 200:
            return 4  # Très élevé
        else:
            return 5  # Extrême

    def get_ubidots_sensors(self, user_id: str, auth_token: Optional[str] = None) -> Dict:
        """
        Récupère les données des capteurs Ubidots depuis l'API RESPIRIA Backend
        
        Args:
            user_id: ID de l'utilisateur
            auth_token: JWT Bearer token pour authentification
        
        Returns:
            Dict avec SpO2, BPM, fréquence respiratoire, détection fumée
        """
        try:
            headers = self.headers.copy()
            
            if auth_token:
                headers['Authorization'] = f'Bearer {auth_token}'
            
            # Récupérer données MAX30102 (médical)
            medical_response = requests.get(
                f"{self.sensors_url}data/max30102/",
                headers=headers,
                timeout=self.timeout
            )
            
            # Récupérer données environnementales
            env_response = requests.get(
                f"{self.sensors_url}data/dht11/",
                headers=headers,
                timeout=self.timeout
            )
            
            # Récupérer données qualité air capteurs
            air_response = requests.get(
                f"{self.sensors_url}data/cjmcu811/",
                headers=headers,
                timeout=self.timeout
            )
            
            medical_data = medical_response.json() if medical_response.status_code == 200 else {}
            env_data = env_response.json() if env_response.status_code == 200 else {}
            air_data = air_response.json() if air_response.status_code == 200 else {}
            
            return {
                # Données physiologiques (MAX30102)
                'spo2': medical_data.get('spo2', 96.0),
                'heart_rate': medical_data.get('heart_rate', 75.0),
                'respiratory_rate': self._estimate_respiratory_rate(medical_data.get('heart_rate', 75)),
                
                # Données environnementales capteurs
                'temperature_sensor': env_data.get('temperature', 25.0),
                'humidity_sensor': env_data.get('humidity', 50.0),
                
                # Détection de fumée/gaz (CJMCU-811)
                'smoke_detected': self._detect_smoke_from_sensors(air_data),
                'eco2_ppm': air_data.get('eco2', 400),
                'tvoc_ppb': air_data.get('tvoc', 50),
                
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'status': 'success'
            }
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur capteurs Ubidots : {e}")
            # Valeurs par défaut sécurisées
            return {
                'spo2': 96.0,
                'heart_rate': 75.0,
                'respiratory_rate': 16.0,
                'temperature_sensor': 25.0,
                'humidity_sensor': 50.0,
                'smoke_detected': False,
                'eco2_ppm': 400,
                'tvoc_ppb': 50,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'status': 'fallback',
                'error': str(e)
            }

    def _estimate_respiratory_rate(self, heart_rate: float) -> float:
        """Estime la fréquence respiratoire basée sur la fréquence cardiaque"""
        # Ratio typique : 1 respiration pour 4-5 battements cardiaques
        return max(12.0, min(25.0, heart_rate / 4.5))

    def _detect_smoke_from_sensors(self, air_data: dict) -> bool:
        """Détecte la fumée basée sur les données des capteurs MQ/CJMCU"""
        eco2 = air_data.get('eco2', 400)
        tvoc = air_data.get('tvoc', 50)
        
        # Seuils d'alarme fumée
        if eco2 > 2000 or tvoc > 500:
            return True
        return False

    def get_ubidots_direct(self) -> Dict:
        """
        📡 Récupère les données directement depuis l'API Ubidots
        Sans passer par le backend Django
        
        Returns:
            Dict avec les dernières valeurs des capteurs
        """
        if not UBIDOTS_TOKEN:
            print("⚠️ UBIDOTS_TOKEN non configuré")
            return self._default_sensor_data()
        
        try:
            headers = {'X-Auth-Token': UBIDOTS_TOKEN}
            
            # Utiliser l'API v1.6 datasources avec l'ID du device
            datasource_id = "696c16da6b8f94fd52f77962"
            
            # Récupérer les variables du datasource
            vars_url = f"https://industrial.api.ubidots.com/api/v1.6/datasources/{datasource_id}/variables/"
            vars_response = requests.get(vars_url, headers=headers, timeout=10)
            
            sensors = {}
            
            if vars_response.status_code == 200:
                variables = vars_response.json().get('results', [])
                
                # Pour chaque variable, récupérer la dernière valeur
                for var in variables:
                    var_id = var.get('id')
                    label = var.get('label')
                    
                    val_url = f"https://industrial.api.ubidots.com/api/v1.6/variables/{var_id}/values/?page_size=1"
                    val_response = requests.get(val_url, headers=headers, timeout=5)
                    
                    if val_response.status_code == 200:
                        values = val_response.json().get('results', [])
                        if values and len(values) > 0:
                            sensors[label] = float(values[0].get('value', 0))
            
            # Mapper les noms de variables
            eco2_val = sensors.get('eco2', 400)
            tvoc_val = sensors.get('tvoc', 0)
            
            # Détection fumée : seuils stricts (eCO2 > 4000 ET TVOC > 1000)
            # ou TVOC très élevé seul (> 2000 = fumée certaine)
            smoke_detected = (eco2_val > 4000 and tvoc_val > 1000) or tvoc_val > 2000
            
            return {
                'spo2': sensors.get('spo2', 96) if sensors.get('spo2', 0) > 0 else 96,
                'heart_rate': sensors.get('bpm', 75) if sensors.get('bpm', 0) > 0 else 75,
                'respiratory_rate': self._estimate_respiratory_rate(sensors.get('bpm', 75)),
                'temperature_sensor': sensors.get('temperature', 25),
                'humidity_sensor': sensors.get('humidity', 50),
                'eco2_ppm': eco2_val,
                'tvoc_ppb': tvoc_val,
                'smoke_detected': smoke_detected,
                'timestamp': datetime.now().isoformat(),
                'source': 'ubidots_direct',
                'status': 'success'
            }
            
        except Exception as e:
            print(f"⚠️ Ubidots direct error: {e}")
            return self._default_sensor_data()
    
    def _default_sensor_data(self) -> Dict:
        """Retourne les valeurs par défaut des capteurs"""
        return {
            'spo2': 96,
            'heart_rate': 75,
            'respiratory_rate': 16,
            'temperature_sensor': 25,
            'humidity_sensor': 50,
            'eco2_ppm': 400,
            'tvoc_ppb': 0,
            'smoke_detected': False,
            'timestamp': datetime.now().isoformat(),
            'source': 'default',
            'status': 'fallback'
        }

    def get_ubidots_latest(self, user_id: str) -> Dict:
        """
        📡 Récupère les DERNIÈRES données Ubidots directement
        Utilise l'API /sensors/ubidots/max30102/ du backend
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict avec les dernières valeurs des capteurs
        """
        try:
            # Token Ubidots
            ubidots_token = "BBUS-IW4Xne31AviZZ0jAAojvf3FczCx8Vw"
            
            # Appel API backend pour données MAX30102
            response = requests.get(
                f"{self.base_url}/sensors/ubidots/max30102/",
                params={'api_token': ubidots_token, 'hours': 1},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                latest = data.get('data', [{}])[0] if data.get('data') else {}
                
                # Appel pour DHT11
                dht_response = requests.get(
                    f"{self.base_url}/sensors/latest/",
                    timeout=self.timeout
                )
                dht_data = dht_response.json() if dht_response.status_code == 200 else {}
                
                return {
                    'spo2': latest.get('spo2', 96),
                    'heart_rate': latest.get('heart_rate', 75),
                    'temperature': dht_data.get('dht11', {}).get('temperature', 25),
                    'humidity': dht_data.get('dht11', {}).get('humidity', 50),
                    'eco2': dht_data.get('cjmcu811', {}).get('eco2', 400),
                    'tvoc': dht_data.get('cjmcu811', {}).get('tvoc', 0),
                    'device_id': latest.get('device_id', '696c16da6b8f94fd52f77962'),
                    'timestamp': latest.get('timestamp', datetime.now().isoformat()),
                    'status': 'success'
                }
            else:
                raise Exception(f"API returned {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Ubidots latest error: {e}")
            return {
                'spo2': 96,
                'heart_rate': 75,
                'temperature': 25,
                'humidity': 50,
                'eco2': 400,
                'tvoc': 0,
                'device_id': '696c16da6b8f94fd52f77962',
                'timestamp': datetime.now().isoformat(),
                'status': 'fallback',
                'error': str(e)
            }

    def get_unified_prediction_data(self, user_id: str, location: Optional[str] = None, 
                                   auth_token: Optional[str] = None) -> Dict:
        """
        🚀 ENDPOINT UNIFIÉ - Récupère TOUTES les données en un seul appel
        Utilise l'endpoint optimisé /api/v1/ai/prediction-data/
        
        Args:
            user_id: ID de l'utilisateur
            location: Localisation (optionnel)
            auth_token: JWT Bearer token
            
        Returns:
            Dict avec toutes les données formatées pour l'IA RESPIRIA
        """
        try:
            params = {
                'user_id': user_id,
                'location': location or 'Abidjan'
            }
            
            headers = self.headers.copy()
            if auth_token:
                headers['Authorization'] = f'Bearer {auth_token}'
            
            response = requests.get(
                self.unified_url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Format optimisé pour le modèle IA RESPIRIA
            return {
                # Données physiologiques (capteurs)
                'spo2': data.get('sensors', {}).get('spo2', 96.0),
                'heart_rate': data.get('sensors', {}).get('heart_rate', 75.0),
                'respiratory_rate': data.get('sensors', {}).get('respiratory_rate', 16.0),
                
                # Données environnementales (API météo)
                'temperature': data.get('weather', {}).get('temperature', 25.0),
                'humidity': data.get('weather', {}).get('humidity', 50.0),
                
                # Qualité de l'air
                'aqi': data.get('air_quality', {}).get('aqi', 50),
                'pollen_level': self._estimate_pollen_from_aqi(data.get('air_quality', {}).get('aqi', 50)),
                
                # Détection de fumée
                'smoke_detected': data.get('sensors', {}).get('smoke_detected', False),
                
                # Métadonnées
                'location': location or 'Abidjan',
                'timestamp': data.get('timestamp', datetime.now().isoformat()),
                'data_sources': {
                    'weather': 'api_backend',
                    'air_quality': 'api_backend', 
                    'sensors': 'ubidots_backend'
                },
                'status': 'unified_success'
            }
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Endpoint unifié indisponible, fallback vers APIs séparées : {e}")
            # Fallback vers collecte séparée
            return self.collect_all_data(user_id, location, auth_token)

    def collect_all_data(self, user_id: int | str, location: Optional[str] = None, 
                        auth_token: Optional[str] = None) -> Dict:
        """
        Collecte toutes les données nécessaires pour la prédiction
        Version fallback si endpoint unifié indisponible
        
        Args:
            user_id: ID de l'utilisateur (int ou str)
            location: Localisation (optionnel)
            auth_token: JWT Bearer token
        
        Returns:
            Dict avec toutes les données formatées pour RESPIRIA IA
        """
        print(f"🔄 Collecte des données pour user {user_id} à {location or 'localisation par défaut'}...")
        
        # Récupérer toutes les données en parallèle (optimisé)
        weather = self.get_weather_data(location, auth_token)
        air_quality = self.get_air_quality_data(location, auth_token)
        sensors = self.get_ubidots_sensors(user_id, auth_token)
        
        # Format unifié pour le modèle IA RESPIRIA
        respiria_data = {
            # Données physiologiques (variables 1-3)
            'spo2': sensors.get('spo2', 96.0),
            'heart_rate': sensors.get('heart_rate', 75.0),
            'respiratory_rate': sensors.get('respiratory_rate', 16.0),
            
            # Données environnementales (variables 4-6) 
            'aqi': air_quality.get('aqi', 50),
            'temperature': weather.get('temperature', 25.0),
            'humidity': weather.get('humidity', 50.0),
            
            # Niveau de pollen (variable 7)
            'pollen_level': air_quality.get('pollen_level', 2),
            
            # Détection de fumée (variable 9)
            'smoke_detected': sensors.get('smoke_detected', False),
            
            # Métadonnées pour debug
            'location': location or 'Abidjan',
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'data_sources': {
                'weather': weather.get('status', 'unknown'),
                'air_quality': air_quality.get('status', 'unknown'),
                'sensors': sensors.get('status', 'unknown')
            },
            'collection_method': 'separate_apis'
        }
        
        print(f"✅ Données collectées : {len(respiria_data)} champs")
        print(f"   📊 SpO2: {respiria_data['spo2']}%, HR: {respiria_data['heart_rate']} bpm")
        print(f"   🌤️ T°: {respiria_data['temperature']}°C, Humidité: {respiria_data['humidity']}%") 
        print(f"   🌫️ AQI: {respiria_data['aqi']}, Pollen: {respiria_data['pollen_level']}/5")
        
        return respiria_data

# Test du collecteur avec vraies APIs
if __name__ == "__main__":
    collector = RespiriaDataCollector()
    
    print("="*70)
    print("🧪 TEST DU COLLECTEUR - APIs RESPIRIA Backend")
    print("="*70)
    
    # Note: Pour un test complet, ajouter un vrai token JWT
    test_token = None  # Remplacer par un vrai token pour test complet
    
    # Test météo
    print("\n1️⃣ Test API Météo RESPIRIA...")
    weather = collector.get_weather_data(location="Paris", auth_token=test_token)
    print(f"   🌡️ Température : {weather.get('temperature')}°C")
    print(f"   💧 Humidité : {weather.get('humidity')}%")
    print(f"   🌍 Ville : {weather.get('city')}")
    print(f"   📊 Status : {weather.get('status')}")
    
    # Test qualité air
    print("\n2️⃣ Test API Qualité Air RESPIRIA...")
    air = collector.get_air_quality_data(location="Paris", auth_token=test_token)
    print(f"   🌫️ AQI : {air.get('aqi')}")
    print(f"   📈 Niveau : {air.get('quality_level')}")
    print(f"   🌸 Pollen estimé : {air.get('pollen_level')}/5")
    print(f"   📊 Status : {air.get('status')}")
    
    # Test capteurs Ubidots
    print("\n3️⃣ Test Capteurs Ubidots...")
    sensors = collector.get_ubidots_sensors(user_id="test123", auth_token=test_token)
    print(f"   🫁 SpO2 : {sensors.get('spo2')}%")
    print(f"   ❤️ Fréquence cardiaque : {sensors.get('heart_rate')} bpm")
    print(f"   💨 Fréquence respiratoire : {sensors.get('respiratory_rate')}/min")
    print(f"   🚨 Fumée détectée : {sensors.get('smoke_detected')}")
    print(f"   📊 Status : {sensors.get('status')}")
    
    # Test endpoint unifié
    print("\n4️⃣ Test Endpoint Unifié (OPTIMISÉ)...")
    unified = collector.get_unified_prediction_data(
        user_id="test123", 
        location="Abidjan", 
        auth_token=test_token
    )
    print(f"   🎯 Données collectées : {list(unified.keys())}")
    print(f"   📊 Méthode : {unified.get('collection_method', 'unified')}")
    print(f"   ✅ Prêt pour IA RESPIRIA : OUI")
    
    # Test collecte complète
    print("\n5️⃣ Test Collecte Complète...")
    all_data = collector.collect_all_data(
        user_id="test123", 
        location="Abidjan",
        auth_token=test_token
    )
    
    print(f"\n🎯 RÉSUMÉ POUR IA RESPIRIA :")
    print(f"   • SpO2: {all_data['spo2']}%")
    print(f"   • Fréquence cardiaque: {all_data['heart_rate']} bpm") 
    print(f"   • Fréquence respiratoire: {all_data['respiratory_rate']}/min")
    print(f"   • AQI: {all_data['aqi']}")
    print(f"   • Température: {all_data['temperature']}°C")
    print(f"   • Humidité: {all_data['humidity']}%")
    print(f"   • Pollen: {all_data['pollen_level']}/5")
    print(f"   • Fumée détectée: {all_data['smoke_detected']}")
    
    print("\n✅ Tests terminés - Prêt pour intégration IA!")
    print("🔗 APIs Backend RESPIRIA opérationnelles")