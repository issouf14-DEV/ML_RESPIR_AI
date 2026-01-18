# api/app.py
"""
API REST RESPIRIA AI - Prédiction de risque d'asthme
"""

try:
    from flask import Flask, request, jsonify  # type: ignore
    from flask_cors import CORS  # type: ignore
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None
    print("⚠️ Flask non installé - API désactivée (pip install flask flask-cors)")

from datetime import datetime
import os

# Charger les variables d'environnement
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass  # dotenv optionnel

# Configuration depuis les variables d'environnement
BACKEND_URL = os.environ.get("RESPIRIA_BACKEND_URL", "https://respira-backend.onrender.com/api/v1")
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# Imports relatifs pour fonctionner avec gunicorn api.app:app
try:
    from .data_collector import RespiriaDataCollector
    from .respiria_ai_predictor import RespiriaAIPredictor
except ImportError:
    # Fallback pour exécution directe (python app.py)
    from data_collector import RespiriaDataCollector
    from respiria_ai_predictor import RespiriaAIPredictor

# Initialiser les services avec l'URL du backend
print("🚀 Initialisation des services RESPIRIA AI...")
print(f"📡 Backend URL: {BACKEND_URL}")
collector = RespiriaDataCollector(base_url=BACKEND_URL)
ai_predictor = RespiriaAIPredictor()
print("✅ Services initialisés")

# Créer l'app Flask si disponible
if FLASK_AVAILABLE:
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/health', methods=['GET'])
    def health():
        """Vérification de santé de l'API"""
        return jsonify({
            'status': 'healthy',
            'model': 'RESPIRIA AI System v1.0',
            'services': {
                'data_collector': 'ready',
                'ai_predictor': 'ready'
            },
            'timestamp': datetime.now().isoformat()
        })

    @app.route('/predict/auto', methods=['POST'])
    def predict_auto():
        """
        Prédiction automatique RESPIRIA avec vraies APIs Backend
        
        Body JSON:
        {
            "user_id": "user123",
            "profile_id": 1,
            "location": "Abidjan",
            "medication_taken": true,
            "auth_token": "Bearer_JWT_Token",
            "sensor_override": {"spo2": 95}
        }
        """
        try:
            data = request.json
            
            if 'user_id' not in data:
                return jsonify({'error': 'user_id requis'}), 400
            
            if 'profile_id' not in data:
                return jsonify({'error': 'profile_id requis (0-3)'}), 400
            
            user_id = data['user_id']
            profile_id = int(data['profile_id'])
            location = data.get('location', 'Abidjan')
            medication_taken = data.get('medication_taken', True)
            auth_token = data.get('auth_token')
            sensor_override = data.get('sensor_override', {})
            
            if profile_id not in [0, 1, 2, 3]:
                return jsonify({'error': 'profile_id doit être 0, 1, 2 ou 3'}), 400
            
            # Collecte des données
            print(f"🚀 Collecte pour {user_id} à {location}...")
            try:
                sensor_data = collector.get_unified_prediction_data(user_id, location, auth_token)
            except Exception as e:
                print(f"⚠️ Fallback collecte: {e}")
                sensor_data = collector.collect_all_data(user_id, location, auth_token)
            
            # Construire données RESPIRIA
            respiria_data = {
                'spo2': sensor_override.get('spo2', sensor_data.get('spo2', 96.0)),
                'heart_rate': sensor_override.get('heart_rate', sensor_data.get('heart_rate', 75.0)),
                'respiratory_rate': sensor_override.get('respiratory_rate', sensor_data.get('respiratory_rate', 16.0)),
                'aqi': sensor_data.get('aqi', 50.0),
                'temperature': sensor_data.get('temperature', 25.0),
                'humidity': sensor_data.get('humidity', 50.0),
                'pollen_level': sensor_data.get('pollen_level', 2),
                'smoke_detected': sensor_override.get('smoke_detected', sensor_data.get('smoke_detected', False)),
                'medication_taken': medication_taken,
                'profile_id': profile_id
            }
            
            # Prédiction
            print(f"🧠 Prédiction RESPIRIA AI (Profil {profile_id})...")
            result = ai_predictor.predict(respiria_data)
            
            if result.get('success'):
                result['api_metadata'] = {
                    'user_id': user_id,
                    'location': location,
                    'api_timestamp': datetime.now().isoformat()
                }
            
            return jsonify(result)
        
        except Exception as e:
            print(f"❌ Erreur prédiction auto: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/predict/manual', methods=['POST'])
    def predict_manual():
        """
        Prédiction manuelle avec les 10 variables
        """
        try:
            data = request.json
            
            required = [
                'spo2', 'heart_rate', 'respiratory_rate', 
                'aqi', 'temperature', 'humidity', 'pollen_level',
                'medication_taken', 'smoke_detected', 'profile_id'
            ]
            
            for field in required:
                if field not in data:
                    return jsonify({'error': f'Champ manquant: {field}'}), 400
            
            profile_id = int(data['profile_id'])
            
            if profile_id not in [0, 1, 2, 3]:
                return jsonify({'error': 'profile_id doit être 0, 1, 2 ou 3'}), 400
            
            print(f"🧠 Prédiction manuelle (Profil {profile_id})...")
            result = ai_predictor.predict(data)
            
            if result.get('success'):
                result['api_metadata'] = {
                    'prediction_type': 'manual',
                    'api_timestamp': datetime.now().isoformat()
                }
            
            return jsonify(result)
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/data/weather', methods=['GET'])
    def get_weather():
        """Récupérer données météo"""
        location = request.args.get('location', 'Abidjan')
        auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        weather = collector.get_weather_data(location, auth_token)
        return jsonify(weather)

    @app.route('/data/air-quality', methods=['GET'])
    def get_air_quality():
        """Récupérer données qualité air"""
        location = request.args.get('location', 'Abidjan')
        auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        air_quality = collector.get_air_quality_data(location, auth_token)
        return jsonify(air_quality)

    @app.route('/data/sensors', methods=['GET'])
    def get_sensors():
        """Récupérer données capteurs Ubidots"""
        user_id = request.args.get('user_id', 'test_user')
        auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        sensors = collector.get_ubidots_sensors(user_id, auth_token)
        return jsonify(sensors)

    @app.route('/data/unified', methods=['GET'])
    def get_unified_data():
        """Endpoint unifié - Toutes les données"""
        user_id = request.args.get('user_id', 'test_user')
        location = request.args.get('location', 'Abidjan')
        auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        unified_data = collector.get_unified_prediction_data(user_id, location, auth_token)
        return jsonify(unified_data)

else:
    app = None
    print("⚠️ Flask non disponible - Installez avec: pip install flask flask-cors")


def main():
    """Point d'entrée principal"""
    if not FLASK_AVAILABLE:
        print("❌ Flask requis pour l'API. Installez avec: pip install flask flask-cors")
        return
    
    port = int(os.environ.get('PORT', 5000))
    print(f"\n🚀 RESPIRIA AI API démarrée sur http://0.0.0.0:{port}")
    print(f"\n📡 Endpoints:")
    print(f"   GET  /health           - Santé")
    print(f"   POST /predict/auto     - Prédiction auto")
    print(f"   POST /predict/manual   - Prédiction manuelle")
    print(f"   GET  /data/weather     - Météo")
    print(f"   GET  /data/air-quality - Qualité air")
    print(f"   GET  /data/sensors     - Capteurs")
    print(f"   GET  /data/unified     - Données unifiées")
    print()
    app.run(host='0.0.0.0', port=port, debug=True)


if __name__ == '__main__':
    main()
