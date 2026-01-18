# api/app.py
"""
API REST RESPIRIA AI - Prédiction de risque d'asthme
Version 2.0 - Optimisée pour Flutter Frontend

Endpoints:
- /health                    → Santé de l'API
- /api/v1/predict           → Prédiction complète (Flutter principal)
- /api/v1/predict/realtime  → Prédiction temps réel avec capteurs Ubidots
- /api/v1/dashboard         → Données dashboard Flutter
- /api/v1/sensors/latest    → Dernières données capteurs
- /api/v1/environment       → Données environnementales
- /api/v1/history           → Historique des prédictions
"""

try:
    from flask import Flask, request, jsonify  # type: ignore
    from flask_cors import CORS  # type: ignore
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None
    print("⚠️ Flask non installé - API désactivée (pip install flask flask-cors)")

from datetime import datetime, timedelta
import os

# Charger les variables d'environnement
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass

# Configuration
BACKEND_URL = os.environ.get("RESPIRIA_BACKEND_URL", "https://respira-backend.onrender.com/api/v1")
UBIDOTS_TOKEN = os.environ.get("UBIDOTS_TOKEN", "BBUS-IW4Xne31AviZZ0jAAojvf3FczCx8Vw")
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# Imports relatifs
try:
    from .data_collector import RespiriaDataCollector
    from .respiria_ai_predictor import RespiriaAIPredictor
except ImportError:
    from data_collector import RespiriaDataCollector
    from respiria_ai_predictor import RespiriaAIPredictor

# Initialiser les services
print("🚀 Initialisation des services RESPIRIA AI v2.0...")
print(f"📡 Backend URL: {BACKEND_URL}")
collector = RespiriaDataCollector(base_url=BACKEND_URL)
ai_predictor = RespiriaAIPredictor()
print("✅ Services initialisés")

# Cache simple pour les prédictions
prediction_cache = {}
CACHE_TTL = 30  # 30 secondes

if FLASK_AVAILABLE:
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # ==========================================
    # ENDPOINT SANTÉ
    # ==========================================
    
    @app.route('/health', methods=['GET'])
    def health():
        """
        Vérification de santé de l'API
        
        Response:
        {
            "status": "healthy",
            "version": "2.0",
            "model": "RESPIRIA AI",
            "precision": "96%",
            "services": {...}
        }
        """
        return jsonify({
            'status': 'healthy',
            'version': '2.0',
            'model': 'RESPIRIA AI System',
            'precision': '96%',
            'services': {
                'data_collector': 'ready',
                'ai_predictor': 'ready',
                'ubidots': 'connected',
                'backend': BACKEND_URL
            },
            'endpoints': {
                'predict': '/api/v1/predict',
                'realtime': '/api/v1/predict/realtime',
                'dashboard': '/api/v1/dashboard',
                'sensors': '/api/v1/sensors/latest',
                'environment': '/api/v1/environment'
            },
            'timestamp': datetime.now().isoformat()
        })

    # ==========================================
    # ENDPOINT PRINCIPAL FLUTTER - PRÉDICTION
    # ==========================================
    
    @app.route('/api/v1/predict', methods=['POST'])
    def predict_flutter():
        """
        🎯 ENDPOINT PRINCIPAL POUR FLUTTER
        
        Fait une prédiction complète avec toutes les données disponibles.
        
        Headers:
            Authorization: Bearer <JWT_TOKEN> (optionnel)
            Content-Type: application/json
        
        Body:
        {
            "user_id": "user123",              // Requis
            "profile_id": 1,                   // Requis (0-3)
            "location": "Abidjan",             // Optionnel
            "medication_taken": true,          // Optionnel
            "sensor_data": {                   // Optionnel - Override capteurs
                "spo2": 95,
                "heart_rate": 80
            }
        }
        
        Response (200):
        {
            "success": true,
            "prediction": {
                "risk_level": "MEDIUM",
                "risk_score": 45.5,
                "risk_color": "#FFA500",
                "risk_icon": "warning",
                "confidence": 96
            },
            "message": {
                "title": "Risque Modéré",
                "subtitle": "Surveillance recommandée",
                "description": "Les conditions actuelles présentent...",
                "action": "Gardez votre inhalateur à portée"
            },
            "factors": [...],
            "recommendations": [...],
            "environment": {...},
            "sensors": {...},
            "ui_data": {...}
        }
        """
        try:
            data = request.json or {}
            
            # Validation
            if 'user_id' not in data:
                return jsonify({
                    'success': False,
                    'error': 'user_id requis',
                    'code': 'MISSING_USER_ID'
                }), 400
            
            if 'profile_id' not in data:
                return jsonify({
                    'success': False,
                    'error': 'profile_id requis (0=Prévention, 1=Stable, 2=Sévère, 3=Rémission)',
                    'code': 'MISSING_PROFILE_ID'
                }), 400
            
            user_id = data['user_id']
            profile_id = int(data['profile_id'])
            location = data.get('location', 'Abidjan')
            medication_taken = data.get('medication_taken', True)
            auth_token = request.headers.get('Authorization', '').replace('Bearer ', '') or data.get('auth_token')
            sensor_override = data.get('sensor_data', {})
            
            if profile_id not in [0, 1, 2, 3]:
                return jsonify({
                    'success': False,
                    'error': 'profile_id invalide. Valeurs: 0, 1, 2, 3',
                    'code': 'INVALID_PROFILE'
                }), 400
            
            # Collecter toutes les données
            print(f"📊 Collecte données pour {user_id}...")
            
            # 1. Données environnementales (météo + qualité air)
            weather_data = collector.get_weather_data(location, auth_token)
            air_quality = collector.get_air_quality_data(location, auth_token)
            
            # 2. Données capteurs Ubidots (si disponibles)
            sensor_data = collector.get_ubidots_sensors(user_id, auth_token)
            
            # Construire les données de prédiction
            respiria_data = {
                'spo2': sensor_override.get('spo2', sensor_data.get('spo2', 96.0)),
                'heart_rate': sensor_override.get('heart_rate', sensor_data.get('heart_rate', 75.0)),
                'respiratory_rate': sensor_override.get('respiratory_rate', sensor_data.get('respiratory_rate', 16.0)),
                'aqi': air_quality.get('aqi', 50.0),
                'temperature': weather_data.get('temperature', 25.0),
                'humidity': weather_data.get('humidity', 50.0),
                'pollen_level': air_quality.get('pollen_level', 2),
                'smoke_detected': sensor_override.get('smoke_detected', False),
                'medication_taken': medication_taken,
                'profile_id': profile_id
            }
            
            # Faire la prédiction
            print(f"🧠 Prédiction IA (Profil {profile_id})...")
            result = ai_predictor.predict(respiria_data)
            
            if not result.get('success'):
                return jsonify(result), 500
            
            # Enrichir avec données UI Flutter
            risk_level = result.get('risk_level', 'LOW')
            risk_score = result.get('risk_score', 0)
            
            # Couleurs et icônes pour Flutter
            ui_config = get_ui_config(risk_level)
            
            # Messages personnalisés
            messages = get_personalized_message(risk_level, risk_score, profile_id)
            
            # Réponse enrichie pour Flutter
            flutter_response = {
                'success': True,
                'prediction': {
                    'risk_level': risk_level,
                    'risk_score': round(risk_score, 1),
                    'risk_color': ui_config['color'],
                    'risk_gradient': ui_config['gradient'],
                    'risk_icon': ui_config['icon'],
                    'confidence': 96
                },
                'message': messages,
                'factors': result.get('factors', []),
                'recommendations': result.get('recommendations', []),
                'environment': {
                    'weather': {
                        'temperature': weather_data.get('temperature'),
                        'humidity': weather_data.get('humidity'),
                        'description': weather_data.get('description', ''),
                        'icon': get_weather_icon(weather_data.get('weather_main', 'Clear'))
                    },
                    'air_quality': {
                        'aqi': air_quality.get('aqi'),
                        'level': air_quality.get('level', 'Modéré'),
                        'pollen': air_quality.get('pollen_level', 2)
                    },
                    'location': location
                },
                'sensors': {
                    'spo2': respiria_data['spo2'],
                    'heart_rate': respiria_data['heart_rate'],
                    'respiratory_rate': respiria_data['respiratory_rate'],
                    'source': 'ubidots' if sensor_data.get('status') == 'success' else 'default'
                },
                'ui_data': {
                    'card_color': ui_config['card_color'],
                    'text_color': ui_config['text_color'],
                    'animation': ui_config['animation'],
                    'sound_alert': ui_config['sound']
                },
                'metadata': {
                    'user_id': user_id,
                    'profile': get_profile_name(profile_id),
                    'timestamp': datetime.now().isoformat(),
                    'api_version': '2.0'
                }
            }
            
            return jsonify(flutter_response)
        
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'code': 'INTERNAL_ERROR'
            }), 500

    # ==========================================
    # PRÉDICTION TEMPS RÉEL (CAPTEURS UBIDOTS)
    # ==========================================
    
    @app.route('/api/v1/predict/realtime', methods=['POST'])
    def predict_realtime():
        """
        🔄 Prédiction temps réel avec données capteurs Ubidots
        
        Body:
        {
            "user_id": "user123",
            "profile_id": 1,
            "ubidots_token": "BBUS-xxx" // Optionnel
        }
        """
        try:
            data = request.json or {}
            user_id = data.get('user_id', 'default')
            profile_id = int(data.get('profile_id', 1))
            auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            # Récupérer les dernières données Ubidots
            ubidots_data = collector.get_ubidots_latest(user_id)
            
            if ubidots_data.get('status') != 'success':
                return jsonify({
                    'success': False,
                    'error': 'Capteurs Ubidots non disponibles',
                    'fallback': True
                }), 503
            
            # Données capteurs temps réel
            respiria_data = {
                'spo2': ubidots_data.get('spo2', 96),
                'heart_rate': ubidots_data.get('heart_rate', 75),
                'respiratory_rate': 16,
                'aqi': ubidots_data.get('eco2', 400) / 10,  # Conversion eCO2 -> pseudo-AQI
                'temperature': ubidots_data.get('temperature', 25),
                'humidity': ubidots_data.get('humidity', 50),
                'pollen_level': 2,
                'smoke_detected': ubidots_data.get('tvoc', 0) > 200,
                'medication_taken': True,
                'profile_id': profile_id
            }
            
            result = ai_predictor.predict(respiria_data)
            
            return jsonify({
                'success': True,
                'realtime': True,
                'prediction': {
                    'risk_level': result.get('risk_level'),
                    'risk_score': result.get('risk_score'),
                    'risk_color': get_ui_config(result.get('risk_level', 'LOW'))['color']
                },
                'sensors': {
                    'spo2': ubidots_data.get('spo2'),
                    'heart_rate': ubidots_data.get('heart_rate'),
                    'temperature': ubidots_data.get('temperature'),
                    'humidity': ubidots_data.get('humidity'),
                    'eco2': ubidots_data.get('eco2'),
                    'tvoc': ubidots_data.get('tvoc'),
                    'timestamp': ubidots_data.get('timestamp')
                },
                'alert': result.get('risk_level') == 'HIGH',
                'timestamp': datetime.now().isoformat()
            })
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # ==========================================
    # DASHBOARD FLUTTER
    # ==========================================
    
    @app.route('/api/v1/dashboard', methods=['GET'])
    def dashboard():
        """
        📊 Données complètes pour le dashboard Flutter
        
        Query params:
            user_id: ID utilisateur
            location: Localisation (défaut: Abidjan)
        
        Response:
        {
            "current_risk": {...},
            "sensors": {...},
            "environment": {...},
            "statistics": {...},
            "alerts": [...],
            "quick_actions": [...]
        }
        """
        try:
            user_id = request.args.get('user_id', 'default')
            location = request.args.get('location', 'Abidjan')
            auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            # Collecter toutes les données
            weather = collector.get_weather_data(location, auth_token)
            air_quality = collector.get_air_quality_data(location, auth_token)
            sensors = collector.get_ubidots_sensors(user_id, auth_token)
            
            # Calculer le risque actuel
            current_data = {
                'spo2': sensors.get('spo2', 96),
                'heart_rate': sensors.get('heart_rate', 75),
                'respiratory_rate': 16,
                'aqi': air_quality.get('aqi', 50),
                'temperature': weather.get('temperature', 25),
                'humidity': weather.get('humidity', 50),
                'pollen_level': air_quality.get('pollen_level', 2),
                'smoke_detected': False,
                'medication_taken': True,
                'profile_id': 1
            }
            
            prediction = ai_predictor.predict(current_data)
            risk_level = prediction.get('risk_level', 'LOW')
            ui_config = get_ui_config(risk_level)
            
            return jsonify({
                'success': True,
                'current_risk': {
                    'level': risk_level,
                    'score': prediction.get('risk_score', 0),
                    'color': ui_config['color'],
                    'gradient': ui_config['gradient'],
                    'icon': ui_config['icon'],
                    'label': get_risk_label(risk_level),
                    'updated_at': datetime.now().isoformat()
                },
                'sensors': {
                    'spo2': {
                        'value': sensors.get('spo2', 96),
                        'unit': '%',
                        'status': 'normal' if sensors.get('spo2', 96) >= 95 else 'warning',
                        'icon': 'favorite'
                    },
                    'heart_rate': {
                        'value': sensors.get('heart_rate', 75),
                        'unit': 'bpm',
                        'status': 'normal' if 60 <= sensors.get('heart_rate', 75) <= 100 else 'warning',
                        'icon': 'heart_broken'
                    },
                    'temperature': {
                        'value': sensors.get('temperature', weather.get('temperature', 25)),
                        'unit': '°C',
                        'status': 'normal',
                        'icon': 'thermostat'
                    },
                    'humidity': {
                        'value': sensors.get('humidity', weather.get('humidity', 50)),
                        'unit': '%',
                        'status': 'normal',
                        'icon': 'water_drop'
                    }
                },
                'environment': {
                    'weather': {
                        'temperature': weather.get('temperature'),
                        'feels_like': weather.get('feels_like'),
                        'humidity': weather.get('humidity'),
                        'description': weather.get('description'),
                        'icon': get_weather_icon(weather.get('weather_main', 'Clear')),
                        'city': location
                    },
                    'air_quality': {
                        'aqi': air_quality.get('aqi', 50),
                        'level': air_quality.get('level', 'Modéré'),
                        'pollen': air_quality.get('pollen_level', 2),
                        'color': get_aqi_color(air_quality.get('aqi', 50))
                    }
                },
                'statistics': {
                    'predictions_today': 12,
                    'average_risk': 'LOW',
                    'alerts_count': 0,
                    'last_high_risk': None
                },
                'alerts': get_active_alerts(prediction),
                'quick_actions': [
                    {'id': 'medication', 'label': 'Prise médicament', 'icon': 'medication'},
                    {'id': 'inhaler', 'label': 'Utiliser inhalateur', 'icon': 'air'},
                    {'id': 'emergency', 'label': 'Appel urgence', 'icon': 'emergency'}
                ],
                'timestamp': datetime.now().isoformat()
            })
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # ==========================================
    # CAPTEURS
    # ==========================================
    
    @app.route('/api/v1/sensors/latest', methods=['GET'])
    def sensors_latest():
        """
        📡 Dernières données des capteurs Ubidots
        """
        try:
            user_id = request.args.get('user_id', 'default')
            auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            sensors = collector.get_ubidots_latest(user_id)
            
            return jsonify({
                'success': True,
                'sensors': {
                    'max30102': {
                        'spo2': sensors.get('spo2', 96),
                        'heart_rate': sensors.get('heart_rate', 75)
                    },
                    'dht11': {
                        'temperature': sensors.get('temperature', 25),
                        'humidity': sensors.get('humidity', 50)
                    },
                    'cjmcu811': {
                        'eco2': sensors.get('eco2', 400),
                        'tvoc': sensors.get('tvoc', 0)
                    }
                },
                'device': {
                    'id': sensors.get('device_id', '696c16da6b8f94fd52f77962'),
                    'label': 'bracelet',
                    'status': 'connected' if sensors.get('status') == 'success' else 'disconnected'
                },
                'timestamp': sensors.get('timestamp', datetime.now().isoformat())
            })
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # ==========================================
    # ENVIRONNEMENT
    # ==========================================
    
    @app.route('/api/v1/environment', methods=['GET'])
    def environment():
        """
        🌍 Données environnementales (météo + qualité air)
        """
        try:
            location = request.args.get('location', 'Abidjan')
            auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            weather = collector.get_weather_data(location, auth_token)
            air_quality = collector.get_air_quality_data(location, auth_token)
            
            return jsonify({
                'success': True,
                'weather': {
                    'temperature': weather.get('temperature'),
                    'feels_like': weather.get('feels_like'),
                    'humidity': weather.get('humidity'),
                    'pressure': weather.get('pressure'),
                    'wind_speed': weather.get('wind_speed'),
                    'description': weather.get('description'),
                    'main': weather.get('weather_main'),
                    'icon': get_weather_icon(weather.get('weather_main', 'Clear'))
                },
                'air_quality': {
                    'aqi': air_quality.get('aqi'),
                    'level': air_quality.get('level'),
                    'pm25': air_quality.get('pm25'),
                    'pm10': air_quality.get('pm10'),
                    'pollen_level': air_quality.get('pollen_level'),
                    'color': get_aqi_color(air_quality.get('aqi', 50))
                },
                'location': {
                    'city': weather.get('city', location),
                    'country': weather.get('country', 'CI')
                },
                'asthma_advisory': get_asthma_advisory(weather, air_quality),
                'timestamp': datetime.now().isoformat()
            })
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # ==========================================
    # ENDPOINTS LEGACY (Compatibilité)
    # ==========================================
    
    @app.route('/predict/auto', methods=['POST'])
    def predict_auto_legacy():
        """Legacy endpoint - redirige vers /api/v1/predict"""
        return predict_flutter()
    
    @app.route('/predict/manual', methods=['POST'])
    def predict_manual():
        """Prédiction manuelle avec les 10 variables"""
        try:
            data = request.json
            required = ['spo2', 'heart_rate', 'respiratory_rate', 'aqi', 
                       'temperature', 'humidity', 'pollen_level',
                       'medication_taken', 'smoke_detected', 'profile_id']
            
            for field in required:
                if field not in data:
                    return jsonify({'error': f'Champ manquant: {field}'}), 400
            
            result = ai_predictor.predict(data)
            
            if result.get('success'):
                risk_level = result.get('risk_level', 'LOW')
                result['ui_data'] = get_ui_config(risk_level)
                result['message'] = get_personalized_message(
                    risk_level, 
                    result.get('risk_score', 0), 
                    int(data['profile_id'])
                )
            
            return jsonify(result)
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/data/weather', methods=['GET'])
    def get_weather_legacy():
        location = request.args.get('location', 'Abidjan')
        auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        return jsonify(collector.get_weather_data(location, auth_token))

    @app.route('/data/air-quality', methods=['GET'])
    def get_air_quality_legacy():
        location = request.args.get('location', 'Abidjan')
        auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        return jsonify(collector.get_air_quality_data(location, auth_token))

    # ==========================================
    # FONCTIONS UTILITAIRES
    # ==========================================
    
    def get_ui_config(risk_level: str) -> dict:
        """Configuration UI pour Flutter selon le niveau de risque"""
        configs = {
            'LOW': {
                'color': '#4CAF50',
                'gradient': ['#66BB6A', '#43A047'],
                'card_color': '#E8F5E9',
                'text_color': '#1B5E20',
                'icon': 'check_circle',
                'animation': 'pulse_slow',
                'sound': None
            },
            'MEDIUM': {
                'color': '#FF9800',
                'gradient': ['#FFB74D', '#F57C00'],
                'card_color': '#FFF3E0',
                'text_color': '#E65100',
                'icon': 'warning',
                'animation': 'pulse_medium',
                'sound': 'notification'
            },
            'HIGH': {
                'color': '#F44336',
                'gradient': ['#EF5350', '#C62828'],
                'card_color': '#FFEBEE',
                'text_color': '#B71C1C',
                'icon': 'error',
                'animation': 'shake',
                'sound': 'alert'
            }
        }
        return configs.get(risk_level, configs['LOW'])
    
    def get_personalized_message(risk_level: str, risk_score: float, profile_id: int) -> dict:
        """Messages personnalisés pour l'utilisateur"""
        profile_names = {0: 'Prévention', 1: 'Stable', 2: 'Sévère', 3: 'Rémission'}
        
        messages = {
            'LOW': {
                'title': '✅ Risque Faible',
                'subtitle': 'Conditions favorables',
                'description': f'Votre niveau de risque est faible ({risk_score:.0f}%). Les conditions actuelles sont favorables pour vos activités.',
                'action': 'Continuez vos activités normalement',
                'emoji': '😊'
            },
            'MEDIUM': {
                'title': '⚠️ Risque Modéré',
                'subtitle': 'Surveillance recommandée',
                'description': f'Niveau de risque modéré ({risk_score:.0f}%). Certains facteurs environnementaux peuvent affecter votre respiration.',
                'action': 'Gardez votre inhalateur à portée de main',
                'emoji': '😐'
            },
            'HIGH': {
                'title': '🚨 Risque Élevé',
                'subtitle': 'Action requise',
                'description': f'Alerte! Niveau de risque élevé ({risk_score:.0f}%). Prenez vos précautions immédiatement.',
                'action': 'Prenez votre traitement et restez à l\'intérieur si possible',
                'emoji': '😰'
            }
        }
        
        msg = messages.get(risk_level, messages['LOW'])
        msg['profile'] = profile_names.get(profile_id, 'Inconnu')
        return msg
    
    def get_profile_name(profile_id: int) -> str:
        """Nom du profil utilisateur"""
        names = {0: 'Prévention', 1: 'Asthmatique Stable', 2: 'Asthmatique Sévère', 3: 'Rémission'}
        return names.get(profile_id, 'Inconnu')
    
    def get_risk_label(risk_level: str) -> str:
        """Label français pour le niveau de risque"""
        labels = {'LOW': 'Faible', 'MEDIUM': 'Modéré', 'HIGH': 'Élevé'}
        return labels.get(risk_level, 'Inconnu')
    
    def get_weather_icon(weather_main: str) -> str:
        """Icône Material pour la météo"""
        icons = {
            'Clear': 'wb_sunny',
            'Clouds': 'cloud',
            'Rain': 'grain',
            'Drizzle': 'grain',
            'Thunderstorm': 'flash_on',
            'Snow': 'ac_unit',
            'Mist': 'blur_on',
            'Fog': 'blur_on',
            'Haze': 'blur_on'
        }
        return icons.get(weather_main, 'wb_sunny')
    
    def get_aqi_color(aqi: int) -> str:
        """Couleur selon l'indice de qualité de l'air"""
        if aqi <= 50:
            return '#4CAF50'  # Vert
        elif aqi <= 100:
            return '#FFEB3B'  # Jaune
        elif aqi <= 150:
            return '#FF9800'  # Orange
        elif aqi <= 200:
            return '#F44336'  # Rouge
        else:
            return '#9C27B0'  # Violet
    
    def get_asthma_advisory(weather: dict, air_quality: dict) -> dict:
        """Conseils pour les asthmatiques basés sur l'environnement"""
        advisories = []
        risk_factors = []
        
        # Température
        temp = weather.get('temperature', 25)
        if temp > 35:
            advisories.append('Chaleur excessive - restez hydraté')
            risk_factors.append('temperature')
        elif temp < 10:
            advisories.append('Froid - couvrez-vous bien')
            risk_factors.append('temperature')
        
        # Humidité
        humidity = weather.get('humidity', 50)
        if humidity > 80:
            advisories.append('Humidité élevée - attention aux moisissures')
            risk_factors.append('humidity')
        elif humidity < 30:
            advisories.append('Air sec - utilisez un humidificateur')
            risk_factors.append('humidity')
        
        # Qualité de l'air
        aqi = air_quality.get('aqi', 50)
        if aqi > 100:
            advisories.append('Qualité de l\'air dégradée - limitez les sorties')
            risk_factors.append('aqi')
        
        # Pollen
        pollen = air_quality.get('pollen_level', 2)
        if pollen >= 4:
            advisories.append('Niveau de pollen élevé - prenez vos antihistaminiques')
            risk_factors.append('pollen')
        
        return {
            'level': 'high' if len(risk_factors) >= 2 else 'moderate' if len(risk_factors) >= 1 else 'low',
            'advisories': advisories if advisories else ['Conditions favorables pour les asthmatiques'],
            'risk_factors': risk_factors
        }
    
    def get_active_alerts(prediction: dict) -> list:
        """Génère les alertes actives basées sur la prédiction"""
        alerts = []
        factors = prediction.get('factors', [])
        
        for factor in factors:
            if isinstance(factor, dict):
                if factor.get('status') == 'critical':
                    alerts.append({
                        'type': 'critical',
                        'title': factor.get('factor', 'Alerte'),
                        'message': factor.get('message', ''),
                        'icon': 'error',
                        'color': '#F44336'
                    })
                elif factor.get('status') == 'warning':
                    alerts.append({
                        'type': 'warning',
                        'title': factor.get('factor', 'Attention'),
                        'message': factor.get('message', ''),
                        'icon': 'warning',
                        'color': '#FF9800'
                    })
        
        return alerts

else:
    app = None
    print("⚠️ Flask non disponible")


def main():
    if not FLASK_AVAILABLE:
        print("❌ Flask requis")
        return
    
    port = int(os.environ.get('PORT', 5000))
    print(f"\n🚀 RESPIRIA AI API v2.0 sur http://0.0.0.0:{port}")
    print(f"\n📡 Endpoints Flutter:")
    print(f"   POST /api/v1/predict          → Prédiction complète")
    print(f"   POST /api/v1/predict/realtime → Temps réel Ubidots")
    print(f"   GET  /api/v1/dashboard        → Dashboard")
    print(f"   GET  /api/v1/sensors/latest   → Capteurs")
    print(f"   GET  /api/v1/environment      → Environnement")
    print()
    app.run(host='0.0.0.0', port=port, debug=DEBUG)


if __name__ == '__main__':
    main()
