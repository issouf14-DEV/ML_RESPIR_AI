# test_simple.py - Test simple pour identifier les besoins d'API
"""
Test simple pour montrer :
1. Les recommandations clairement affichées 
2. Les formats d'API nécessaires
"""

import json
from api.respiria_ai_predictor import RespiriaAIPredictor

def print_recommendations_clearly(result):
    """Affiche les recommandations de façon très claire pour l'utilisateur"""
    if not result.get('success'):
        print(f"❌ Erreur: {result.get('error')}")
        return
    
    recs = result['recommendations']
    
    print("\n" + "="*60)
    print("💡 RECOMMANDATIONS POUR L'UTILISATEUR")
    print("="*60)
    
    # Actions immédiates (URGENTES)
    if recs['immediate']:
        print("\n🚨 ACTIONS IMMÉDIATES À FAIRE MAINTENANT:")
        print("-" * 50)
        for i, action in enumerate(recs['immediate'], 1):
            print(f"   {i}. {action}")
        print()
    
    # Actions préventives 
    if recs['preventive']:
        print("🛡️ ACTIONS PRÉVENTIVES RECOMMANDÉES:")
        print("-" * 50)
        for i, action in enumerate(recs['preventive'], 1):
            print(f"   {i}. {action}")
        print()
    
    # Conseils environnementaux
    if recs['environmental']:
        print("🌍 CONSEILS POUR VOTRE ENVIRONNEMENT:")
        print("-" * 50)
        for i, action in enumerate(recs['environmental'], 1):
            print(f"   {i}. {action}")
        print()
    
    if not any([recs['immediate'], recs['preventive'], recs['environmental']]):
        print("✅ Aucune action particulière nécessaire pour le moment")
        print("   Continuez à surveiller votre état de santé.")

def main():
    print("🧪 TEST SIMPLE - RECOMMANDATIONS ET BESOINS API")
    print("="*70)
    
    predictor = RespiriaAIPredictor()
    
    # Test avec situation critique pour voir toutes les recommandations
    print("\n📋 TEST : Situation avec beaucoup de recommandations")
    
    test_data = {
        'spo2': 89,           # SpO2 bas
        'heart_rate': 110,    # Fréquence cardiaque élevée
        'respiratory_rate': 28, # Fréquence respiratoire élevée
        'aqi': 175,           # Qualité d'air très mauvaise
        'temperature': 8,     # Froid
        'humidity': 85,       # Humidité très élevée
        'pollen_level': 4,    # Pollen très élevé
        'medication_taken': False, # Pas de médicament
        'smoke_detected': False,
        'profile_id': 2       # Asthmatique sévère
    }
    
    result = predictor.predict(test_data)
    
    # Afficher le score et niveau
    pred = result['prediction']
    print(f"\n🎯 RÉSULTAT DE PRÉDICTION:")
    print(f"   Score de risque: {pred['risk_score']}%")
    print(f"   Niveau: {pred['risk_level'].upper()}")
    print(f"   Notification nécessaire: {'OUI' if pred['should_notify'] else 'NON'}")
    
    # Afficher les recommandations clairement
    print_recommendations_clearly(result)
    
    print("\n" + "="*70)
    print("📡 BESOINS D'API POUR TON BACKEND")
    print("="*70)
    
    print("""
🔗 APIs NÉCESSAIRES à créer dans ton backend Django :

1️⃣ API MÉTÉO (OBLIGATOIRE):
   Endpoint: GET /api/v1/environment/weather/
   Paramètre: ?location=Abidjan
   Format de réponse JSON nécessaire:
   {
       "temperature": 25.5,    // en °C
       "humidity": 65.0,       // en %
       "status": "success"
   }

2️⃣ API QUALITÉ AIR (OBLIGATOIRE):
   Endpoint: GET /api/v1/environment/air-quality/
   Paramètre: ?location=Abidjan  
   Format de réponse JSON nécessaire:
   {
       "aqi": 85,              // Indice qualité air 0-500
       "co2": 420,             // eCO2 en ppm (optionnel)
       "pollen_level": 60,     // Niveau pollen 0-100
       "status": "success"
   }

3️⃣ API CAPTEURS UBIDOTS (FUTURE):
   Endpoint: GET /api/v1/sensors/ubidots/
   Paramètre: ?user_id=user123
   Format de réponse JSON nécessaire:
   {
       "spo2": 96.5,           // SpO2 en %
       "heart_rate": 75,       // BPM
       "respiratory_rate": 16, // respirations/min
       "smoke_detected": false, // Capteur MQ-135/MQ-2
       "timestamp": "2026-01-18T10:30:00Z",
       "status": "success"
   }

⚠️ PROBLÈMES ACTUELS DÉTECTÉS :
   - API météo: Timeout (> 10s)
   - API qualité air: 401 Unauthorized (clé API manquante ?)
   
🔧 SOLUTIONS :
   - Ajouter authentification/clés API
   - Optimiser temps de réponse < 5s
   - Valeurs par défaut si APIs externes échouent
   """)

if __name__ == "__main__":
    main()