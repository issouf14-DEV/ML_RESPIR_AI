# RESPIRIA AI - API Machine Learning

API de prédiction de risque d'asthme basée sur l'IA avec intégration capteurs IoT Ubidots.

## 🚀 Déploiement sur Render

### Étape 1: Configuration GitHub
```bash
cd respiria_project
git init
git add .
git commit -m "Initial commit - RESPIRIA AI ML API"
git branch -M main
git remote add origin https://github.com/issouf14-DEV/ML_RESPIR_AI.git
git push -u origin main
```

### Étape 2: Configuration Render

1. **Connectez votre repo GitHub** à Render
2. **Service Type**: Web Service
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `gunicorn api.app:app --bind 0.0.0.0:$PORT`
5. **Variables d'environnement**:
   - `UBIDOTS_TOKEN` = votre token Ubidots
   - `RESPIRIA_BACKEND_URL` = https://respira-backend.onrender.com/api/v1
   - `PORT` = 10000 (automatique sur Render)

### Étape 3: Test

```bash
curl https://votre-app.onrender.com/health
```

## 📡 Endpoints API

### Health Check
```
GET /health
```

### Prédiction Flutter (Principal)
```
POST /api/v1/predict
Content-Type: application/json

{
  "user_id": 1,
  "profile_id": 1,
  "location": {"latitude": 5.3599, "longitude": -4.0083},
  "medication_taken": true
}
```

**Réponse:**
```json
{
  "success": true,
  "prediction": {
    "risk_level": "LOW",
    "risk_score": 4.0,
    "confidence": 89,
    "should_notify": false
  },
  "factors": [...],
  "recommendations": {
    "immediate": [],
    "preventive": [],
    "environmental": []
  },
  "profile_context": {
    "name": "Asthmatique stable",
    "message": "✅ Votre asthme est bien contrôlé",
    "specific_advice": "..."
  },
  "sensors": {
    "spo2": 98.0,
    "heart_rate": 76.0,
    "eco2": 482.0,
    "tvoc": 12.0,
    "smoke_detected": false
  }
}
```

## 🔧 Installation Locale

1. **Cloner le repo**:
```bash
git clone https://github.com/issouf14-DEV/ML_RESPIR_AI.git
cd ML_RESPIR_AI/respiria_project
```

2. **Créer environnement virtuel**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer dépendances**:
```bash
pip install -r requirements.txt
```

4. **Configurer variables d'environnement**:
```bash
cp .env.example .env
# Éditer .env avec vos valeurs
```

5. **Lancer l'API**:
```bash
python -c "from api.app import app; app.run(host='0.0.0.0', port=5000)"
```

## 🧪 Tests

```bash
# Test avec données réelles Ubidots
python test_flutter_format.py

# Test des 4 profils
python test_profiles_detailed.py

# Monitoring capteurs en temps réel (PowerShell)
.\Monitor-Capteurs.ps1
```

## 📊 Profils Utilisateurs

- **0 - Prévention**: Asthme léger, pas de symptômes
- **1 - Stable**: Asthme contrôlé avec traitement
- **2 - Sévère**: Asthme non contrôlé, crises fréquentes
- **3 - Rémission**: Ancien asthmatique, surveillance

## 🔒 Sécurité

- Tokens stockés dans variables d'environnement
- CORS activé pour Flutter
- Validation des données d'entrée
- Cache de prédictions (30s TTL)

## 📝 Notes de Déploiement

### Erreurs 401 APIs Externes
Les erreurs suivantes sont **normales** et n'empêchent pas le fonctionnement:
```
❌ Erreur API météo : 401 Client Error: Unauthorized
❌ Erreur API qualité air : 401 Client Error: Unauthorized
```

Le système utilise des **valeurs par défaut** quand ces APIs échouent:
- Température: 25°C
- Humidité: 55%
- AQI: 50
- Pollen: 2/5

Les données des **capteurs Ubidots** (SpO2, BPM, eCO2, TVOC) sont récupérées directement et fonctionnent correctement.

## 🌐 Architecture

```
API ML RESPIRIA ← Flutter App
     ↓
     ├─ Ubidots API (capteurs IoT)
     ├─ Backend RESPIRIA (optionnel)
     └─ Modèle IA (local)
```

## 📞 Support

- GitHub: https://github.com/issouf14-DEV/ML_RESPIR_AI
- Backend: https://respira-backend.onrender.com
- ML API: https://ml-respir-ai.onrender.com
