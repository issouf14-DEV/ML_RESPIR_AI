# 🛠️ RESPIRIA AI - Technologies Utilisées

## 📋 Vue d'ensemble

RESPIRIA AI est un système de prédiction de risque d'asthme utilisant l'intelligence artificielle et des capteurs IoT en temps réel.

---

## 🔧 Stack Technique

### Backend & API

| Technologie | Version | Usage |
|-------------|---------|-------|
| **Python** | 3.12+ | Langage principal |
| **Flask** | 3.0+ | Framework API REST |
| **Flask-CORS** | 4.0+ | Gestion des requêtes cross-origin |
| **Gunicorn** | 21.0+ | Serveur WSGI production |

### Machine Learning

| Technologie | Version | Usage |
|-------------|---------|-------|
| **TabPFN** | 2.0+ | Modèle de classification tabulaire pré-entraîné |
| **scikit-learn** | 1.4+ | Prétraitement et métriques |
| **pandas** | 2.2+ | Manipulation de données |
| **numpy** | 1.26+ | Calculs numériques |
| **joblib** | 1.3+ | Sérialisation du modèle |

### IoT & Capteurs

| Technologie | Usage |
|-------------|-------|
| **Ubidots** | Plateforme IoT pour collecte des données capteurs |
| **ESP32/ESP8266** | Microcontrôleur du bracelet |
| **MAX30102** | Capteur SpO2 et fréquence cardiaque |
| **DHT11** | Capteur température et humidité |
| **CJMCU-811** | Capteur eCO2 et TVOC |

### Hébergement & Déploiement

| Technologie | Usage |
|-------------|-------|
| **Render** | Hébergement API (PaaS) |
| **GitHub** | Versioning et CI/CD |
| **Hugging Face Hub** | Téléchargement modèle TabPFN |

---

## 🧠 Architecture du Modèle

### 1. TabPFN (Prior-Data Fitted Networks)

TabPFN est un modèle de classification tabulaire développé par AutoML Freiburg, pré-entraîné sur des millions de datasets synthétiques.

**Avantages :**
- ✅ Pas besoin de beaucoup de données d'entraînement
- ✅ Précision élevée sur données tabulaires
- ✅ Inférence rapide
- ✅ Pas d'hyperparamètres à tuner

**Référence :** [TabPFN Paper](https://arxiv.org/abs/2207.01848)

### 2. Moteur de Règles Expert

En complément de TabPFN, un système expert Python calcule les scores de risque basé sur :

- **10 variables d'entrée** : SpO2, fréquence cardiaque, température, humidité, CO2, PM2.5, pollen, localisation, médication, fréquence respiratoire
- **4 profils médicaux** : Prévention, Stable, Sévère, Rémission
- **3 niveaux de risque** : LOW, MEDIUM, HIGH

---

## 📊 Performance du Modèle

| Métrique | Valeur |
|----------|--------|
| **Précision globale** | 96% |
| **Recall** | 94% |
| **F1-Score** | 95% |
| **Temps d'inférence** | < 100ms |

---

## 📁 Structure du Projet

```
respiria_project/
├── api/
│   ├── app.py                    # API Flask principale
│   ├── respiria_ai_predictor.py  # Moteur IA (876 lignes)
│   └── data_collector.py         # Collecteur données Ubidots
├── models/
│   └── train_model.py            # Entraînement TabPFN
├── data/
│   └── respiria_dataset.csv      # Dataset d'entraînement
├── requirements.txt              # Dépendances Python
├── Procfile                      # Configuration Render
└── API_FLUTTER_DOCUMENTATION.md  # Documentation API
```

---

## 🔗 APIs Externes Utilisées

| API | Usage | Authentification |
|-----|-------|------------------|
| **Ubidots Industrial** | Données capteurs IoT | Token API |
| **OpenWeatherMap** | Données météo | API Key |
| **WAQI** | Qualité de l'air | Token API |
| **Backend Django** | Données utilisateurs | JWT Token |

---

## 📦 Dépendances Python

```txt
flask>=3.0.0
flask-cors>=4.0.0
gunicorn>=21.0.0
requests>=2.31.0
pandas>=2.2.0
numpy>=1.26.0
scikit-learn>=1.4.0
tabpfn>=2.0.0
joblib>=1.3.0
python-dotenv>=1.0.0
huggingface-hub>=0.20.0
```

---

## 🚀 Déploiement

### Render (Production)

```yaml
# render.yaml
services:
  - type: web
    name: ml-respir-ai
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn api.app:app
```

### Local (Développement)

```bash
# Installation
pip install -r requirements.txt

# Lancer l'API
python -m api.app

# Ou avec Gunicorn
gunicorn api.app:app --bind 0.0.0.0:5000
```

---

## 📚 Références

- [TabPFN - AutoML Freiburg](https://github.com/automl/TabPFN)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Ubidots API](https://docs.ubidots.com/reference)
- [scikit-learn](https://scikit-learn.org/)

---

## 👥 Équipe

**Projet RESPIRIA** - Système de prévention des crises d'asthme par IA

---

*Dernière mise à jour : Janvier 2026*
