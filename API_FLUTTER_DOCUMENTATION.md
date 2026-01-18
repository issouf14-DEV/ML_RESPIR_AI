# 📱 RESPIRIA AI - Documentation API Flutter

## 🌐 Base URL
```
https://ml-respir-ai.onrender.com
```

## ✅ Version API
```
Version: 2.0
Status: DEPLOYED
Precision: 96%
```

## 🔐 Authentification
L'API ML ne nécessite pas d'authentification. Le Backend Django nécessite un JWT Token :
```http
Authorization: Bearer <JWT_TOKEN>
```

---

## 📋 Endpoints Disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Vérification santé API |
| `/api/v1/predict` | POST | **Prédiction complète (PRINCIPAL)** |
| `/api/v1/predict/realtime` | POST | Prédiction temps réel Ubidots |
| `/api/v1/dashboard` | GET | Données dashboard Flutter |
| `/api/v1/sensors/latest` | GET | Dernières données capteurs |
| `/api/v1/environment` | GET | Données environnementales |

---

## 🎯 1. Prédiction Complète (Endpoint Principal)

**C'est l'endpoint principal à utiliser dans Flutter pour obtenir une prédiction.**

### Requête
```http
POST /api/v1/predict
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN> (optionnel)
```

### Body
```json
{
    "user_id": "user123",
    "profile_id": 1,
    "location": "Abidjan",
    "medication_taken": true,
    "sensor_data": {
        "spo2": 95,
        "heart_rate": 80
    }
}
```

### Paramètres

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `user_id` | string | ✅ Oui | Identifiant unique de l'utilisateur |
| `profile_id` | int | ✅ Oui | Profil médical (0-3) |
| `location` | string | Non | Ville pour météo/qualité air (défaut: "Abidjan") |
| `medication_taken` | bool | Non | Médicament pris aujourd'hui (défaut: true) |
| `sensor_data` | object | Non | Override des données capteurs |

### Profils Disponibles

| ID | Nom | Description |
|----|-----|-------------|
| 0 | Prévention | Personne saine en prévention |
| 1 | Stable | Asthmatique bien contrôlé |
| 2 | Sévère | Asthmatique nécessitant surveillance |
| 3 | Rémission | Ancien asthmatique en rémission |

### Réponse Succès (200) - EXEMPLE RÉEL
```json
{
    "success": true,
    "prediction": {
        "risk_level": "LOW",
        "risk_score": 0,
        "risk_color": "#4CAF50",
        "risk_gradient": ["#81C784", "#388E3C"],
        "risk_icon": "check_circle",
        "confidence": 96
    },
    "message": {
        "title": "✅ Risque Faible",
        "subtitle": "Conditions favorables",
        "description": "Votre niveau de risque est faible (0%). Les conditions actuelles sont favorables pour vos activités.",
        "action": "Continuez vos activités normalement",
        "emoji": "😊",
        "profile": "Stable"
    },
    "factors": [
        {
            "factor": "Qualité de l'air",
            "value": 85,
            "contribution_percent": 15.2,
            "status": "warning",
            "message": "AQI modéré - Surveillance recommandée"
        }
    ],
    "recommendations": [
        "Évitez les efforts intenses à l'extérieur",
        "Gardez votre inhalateur à portée"
    ],
    "environment": {
        "weather": {
            "temperature": 28.5,
            "humidity": 75,
            "description": "partiellement nuageux",
            "icon": "cloud"
        },
        "air_quality": {
            "aqi": 85,
            "level": "Modéré",
            "pollen": 3
        },
        "location": "Abidjan"
    },
    "sensors": {
        "spo2": 96,
        "heart_rate": 75,
        "respiratory_rate": 16,
        "source": "ubidots"
    },
    "ui_data": {
        "card_color": "#FFF3E0",
        "text_color": "#E65100",
        "animation": "pulse_medium",
        "sound_alert": "notification"
    },
    "metadata": {
        "user_id": "user123",
        "profile": "Asthmatique Stable",
        "timestamp": "2026-01-18T17:30:00.000Z",
        "api_version": "2.0"
    }
}
```

### Réponse Erreur (400/500)
```json
{
    "success": false,
    "error": "user_id requis",
    "code": "MISSING_USER_ID"
}
```

### Exemple Flutter (Dart)
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class RespiriaAPI {
  static const String baseUrl = 'https://ml-respir-ai.onrender.com';
  
  Future<Map<String, dynamic>> predict({
    required String userId,
    required int profileId,
    String location = 'Abidjan',
    bool medicationTaken = true,
    Map<String, dynamic>? sensorData,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/predict'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'profile_id': profileId,
        'location': location,
        'medication_taken': medicationTaken,
        if (sensorData != null) 'sensor_data': sensorData,
      }),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Erreur API: ${response.body}');
    }
  }
}

// Utilisation
final api = RespiriaAPI();
final result = await api.predict(
  userId: 'user123',
  profileId: 1,
  location: 'Abidjan',
);

print('Risque: ${result['prediction']['risk_level']}');
print('Score: ${result['prediction']['risk_score']}');
print('Couleur: ${result['prediction']['risk_color']}');
```

---

## 📊 2. Dashboard

### Requête
```http
GET /api/v1/dashboard?user_id=user123&location=Abidjan
```

### Réponse
```json
{
    "success": true,
    "current_risk": {
        "level": "LOW",
        "score": 18.5,
        "color": "#4CAF50",
        "gradient": ["#66BB6A", "#43A047"],
        "icon": "check_circle",
        "label": "Faible",
        "updated_at": "2026-01-18T17:30:00.000Z"
    },
    "sensors": {
        "spo2": {
            "value": 97,
            "unit": "%",
            "status": "normal",
            "icon": "favorite"
        },
        "heart_rate": {
            "value": 72,
            "unit": "bpm",
            "status": "normal",
            "icon": "heart_broken"
        },
        "temperature": {
            "value": 28,
            "unit": "°C",
            "status": "normal",
            "icon": "thermostat"
        },
        "humidity": {
            "value": 65,
            "unit": "%",
            "status": "normal",
            "icon": "water_drop"
        }
    },
    "environment": {
        "weather": {
            "temperature": 28,
            "feels_like": 31,
            "humidity": 65,
            "description": "ensoleillé",
            "icon": "wb_sunny",
            "city": "Abidjan"
        },
        "air_quality": {
            "aqi": 45,
            "level": "Bon",
            "pollen": 2,
            "color": "#4CAF50"
        }
    },
    "statistics": {
        "predictions_today": 12,
        "average_risk": "LOW",
        "alerts_count": 0,
        "last_high_risk": null
    },
    "alerts": [],
    "quick_actions": [
        {"id": "medication", "label": "Prise médicament", "icon": "medication"},
        {"id": "inhaler", "label": "Utiliser inhalateur", "icon": "air"},
        {"id": "emergency", "label": "Appel urgence", "icon": "emergency"}
    ],
    "timestamp": "2026-01-18T17:30:00.000Z"
}
```

### Exemple Flutter
```dart
Future<Map<String, dynamic>> getDashboard(String userId, String location) async {
  final response = await http.get(
    Uri.parse('$baseUrl/api/v1/dashboard?user_id=$userId&location=$location'),
  );
  return jsonDecode(response.body);
}
```

---

## 📡 3. Capteurs (Dernières données)

### Requête
```http
GET /api/v1/sensors/latest?user_id=user123
```

### Réponse
```json
{
    "success": true,
    "sensors": {
        "max30102": {
            "spo2": 97,
            "heart_rate": 72
        },
        "dht11": {
            "temperature": 28,
            "humidity": 65
        },
        "cjmcu811": {
            "eco2": 450,
            "tvoc": 15
        }
    },
    "device": {
        "id": "696c16da6b8f94fd52f77962",
        "label": "bracelet",
        "status": "connected"
    },
    "timestamp": "2026-01-18T17:30:00.000Z"
}
```

---

## 🌍 4. Environnement

### Requête
```http
GET /api/v1/environment?location=Abidjan
```

### Réponse
```json
{
    "success": true,
    "weather": {
        "temperature": 28,
        "feels_like": 31,
        "humidity": 65,
        "pressure": 1013,
        "wind_speed": 12,
        "description": "ensoleillé",
        "main": "Clear",
        "icon": "wb_sunny"
    },
    "air_quality": {
        "aqi": 45,
        "level": "Bon",
        "pm25": 12,
        "pm10": 25,
        "pollen_level": 2,
        "color": "#4CAF50"
    },
    "location": {
        "city": "Abidjan",
        "country": "CI"
    },
    "asthma_advisory": {
        "level": "low",
        "advisories": ["Conditions favorables pour les asthmatiques"],
        "risk_factors": []
    },
    "timestamp": "2026-01-18T17:30:00.000Z"
}
```

---

## 🔄 5. Prédiction Temps Réel

Pour des mises à jour fréquentes basées sur les capteurs Ubidots.

### Requête
```http
POST /api/v1/predict/realtime
Content-Type: application/json
```

### Body
```json
{
    "user_id": "user123",
    "profile_id": 1
}
```

### Réponse
```json
{
    "success": true,
    "realtime": true,
    "prediction": {
        "risk_level": "LOW",
        "risk_score": 15.2,
        "risk_color": "#4CAF50"
    },
    "sensors": {
        "spo2": 97,
        "heart_rate": 72,
        "temperature": 28,
        "humidity": 65,
        "eco2": 450,
        "tvoc": 15,
        "timestamp": "2026-01-18T17:30:00.000Z"
    },
    "alert": false,
    "timestamp": "2026-01-18T17:30:00.000Z"
}
```

---

## 🎨 Guide UI Flutter

### Couleurs par niveau de risque

```dart
Color getRiskColor(String riskLevel) {
  switch (riskLevel) {
    case 'LOW':
      return Color(0xFF4CAF50);  // Vert
    case 'MEDIUM':
      return Color(0xFFFF9800);  // Orange
    case 'HIGH':
      return Color(0xFFF44336);  // Rouge
    default:
      return Color(0xFF4CAF50);
  }
}
```

### Gradients
```dart
List<Color> getRiskGradient(String riskLevel) {
  switch (riskLevel) {
    case 'LOW':
      return [Color(0xFF66BB6A), Color(0xFF43A047)];
    case 'MEDIUM':
      return [Color(0xFFFFB74D), Color(0xFFF57C00)];
    case 'HIGH':
      return [Color(0xFFEF5350), Color(0xFFC62828)];
    default:
      return [Color(0xFF66BB6A), Color(0xFF43A047)];
  }
}
```

### Icônes Material
```dart
IconData getRiskIcon(String riskLevel) {
  switch (riskLevel) {
    case 'LOW':
      return Icons.check_circle;
    case 'MEDIUM':
      return Icons.warning;
    case 'HIGH':
      return Icons.error;
    default:
      return Icons.check_circle;
  }
}
```

---

## 🔊 Alertes Sonores

| Risque | Son | Fichier |
|--------|-----|---------|
| LOW | Aucun | - |
| MEDIUM | Notification | `notification.mp3` |
| HIGH | Alerte | `alert.mp3` |

---

## ⚡ Bonnes Pratiques

### 1. Caching
```dart
class PredictionCache {
  Map<String, dynamic>? _lastPrediction;
  DateTime? _lastUpdate;
  
  bool shouldRefresh() {
    if (_lastUpdate == null) return true;
    return DateTime.now().difference(_lastUpdate!) > Duration(seconds: 30);
  }
}
```

### 2. Gestion d'erreurs
```dart
try {
  final result = await api.predict(...);
  if (result['success'] == true) {
    // Utiliser les données
  } else {
    // Afficher l'erreur
    showError(result['error']);
  }
} catch (e) {
  // Erreur réseau
  showOfflineMode();
}
```

### 3. Polling temps réel
```dart
Timer.periodic(Duration(seconds: 30), (timer) async {
  final result = await api.getDashboard(userId, location);
  updateUI(result);
});
```

---

## 📞 Support

- **API ML**: https://ml-respir-ai.onrender.com
- **API Backend**: https://respira-backend.onrender.com
- **Health Check**: GET /health

---

## � Données de Test Réelles (Ubidots)

### Capteurs du Bracelet (18/01/2026)
| Capteur | Valeur | Unité | Status |
|---------|--------|-------|--------|
| Temperature | 32.3 | °C | ✅ OK |
| Humidity | 73.0 | % | ✅ OK |
| eCO2 | 436.0 | ppm | ✅ OK |
| TVOC | 5.0 | ppb | ✅ OK |
| SpO2 | 0.0 | % | ⚠️ Calibration requise |
| BPM | 0.0 | bpm | ⚠️ Calibration requise |

### Exemple de Réponse Réelle
```json
{
  "success": true,
  "prediction": {
    "risk_level": "low",
    "risk_score": 6.6,
    "confidence": 0.89,
    "should_notify": false
  },
  "profile_context": {
    "name": "Asthmatique stable",
    "message": "✅ Votre asthme est bien contrôlé, conditions favorables"
  },
  "factors": {
    "pollen_level": "critical"
  }
}
```

### Configuration Ubidots
```dart
const String UBIDOTS_TOKEN = 'BBUS-IW4Xne31AviZZ0jAAojvf3FczCx8Vw';
const String DEVICE_ID = '696c16da6b8f94fd52f77962';
const String DEVICE_LABEL = 'bracelet';
```

---

## �🔗 Liens Utiles

- [Backend Django API Guide](./BACKEND_API_GUIDE.md)
- [Ubidots Token](BBUS-IW4Xne31AviZZ0jAAojvf3FczCx8Vw)
- [Device Bracelet](696c16da6b8f94fd52f77962)
