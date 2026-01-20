"""
Test RESPIRIA - Tous les profils utilisateurs
Vérifie les prédictions et recommandations pour chaque type d'utilisateur
"""
import os
import sys

# Ajouter le chemin pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Charger .env
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass

from api.respiria_ai_predictor import RespiriaAIPredictor

# Initialiser le moteur IA
predictor = RespiriaAIPredictor()

# Profils utilisateurs
PROFILES = {
    0: "Prévention (personne saine)",
    1: "Asthmatique Stable",
    2: "Asthmatique Sévère", 
    3: "Rémission"
}

# Scénarios de test avec données capteurs réelles
SCENARIOS = [
    {
        "name": "🟢 Conditions normales",
        "data": {
            "spo2": 98,
            "heart_rate": 72,
            "respiratory_rate": 14,
            "temperature": 25,
            "humidity": 55,
            "aqi": 35,
            "eco2": 450,
            "tvoc": 30,
            "pollen_level": 1,
            "pm25": 8,       # PM2.5 faible
            "pm10": 15,      # PM10 faible
            "pressure": 1013, # Pression normale
            "wind_speed": 5,  # Vent léger
            "medication_taken": True,
            "smoke_detected": False
        }
    },
    {
        "name": "🟡 CO2 élevé (pièce mal ventilée)",
        "data": {
            "spo2": 96,
            "heart_rate": 78,
            "respiratory_rate": 16,
            "temperature": 28,
            "humidity": 65,
            "aqi": 50,
            "eco2": 1800,  # CO2 élevé!
            "tvoc": 180,
            "pollen_level": 2,
            "pm25": 20,      # PM2.5 modéré
            "pm10": 35,      # PM10 modéré
            "pressure": 1008, # Légère dépression
            "wind_speed": 12, # Vent modéré
            "medication_taken": True,
            "smoke_detected": False
        }
    },
    {
        "name": "🟠 Qualité air dégradée + humidité élevée",
        "data": {
            "spo2": 94,
            "heart_rate": 85,
            "respiratory_rate": 18,
            "temperature": 32,
            "humidity": 82,
            "aqi": 120,
            "eco2": 1200,
            "tvoc": 350,
            "pollen_level": 3,
            "pm25": 45,      # PM2.5 élevé!
            "pm10": 70,      # PM10 élevé
            "pressure": 990,  # Dépression orageuse
            "wind_speed": 25, # Vent fort
            "medication_taken": False,  # Pas de médicament!
            "smoke_detected": False
        }
    },
    {
        "name": "🔴 Situation critique (CO2 + TVOC dangereux)",
        "data": {
            "spo2": 91,
            "heart_rate": 110,
            "respiratory_rate": 24,
            "temperature": 35,
            "humidity": 75,
            "aqi": 180,
            "eco2": 3500,  # CO2 dangereux!
            "tvoc": 800,   # TVOC dangereux!
            "pollen_level": 4,
            "pm25": 60,      # PM2.5 dangereux!
            "pm10": 120,     # PM10 dangereux!
            "pressure": 985,  # Forte dépression
            "wind_speed": 45, # Vent très fort
            "medication_taken": False,
            "smoke_detected": False
        }
    },
    {
        "name": "🚨 URGENCE (fumée détectée)",
        "data": {
            "spo2": 88,
            "heart_rate": 125,
            "respiratory_rate": 28,
            "temperature": 38,
            "humidity": 60,
            "aqi": 250,
            "eco2": 5000,
            "tvoc": 2500,
            "pollen_level": 5,
            "pm25": 80,       # PM2.5 très dangereux!
            "pm10": 150,      # PM10 très dangereux!
            "pressure": 980,   # Très forte dépression
            "wind_speed": 60,  # Tempête!
            "medication_taken": False,
            "smoke_detected": True  # FUMÉE!
        }
    }
]


def test_profile(profile_id: int, scenario: dict):
    """Teste un profil avec un scénario donné"""
    data = scenario["data"].copy()
    data["profile_id"] = profile_id
    
    # Faire la prédiction
    result = predictor.predict(data)
    
    return result


def print_result(result: dict, profile_name: str):
    """Affiche le résultat de manière formatée"""
    if not result.get("success"):
        print(f"    ❌ Erreur: {result.get('error')}")
        return
    
    prediction = result.get("prediction", {})
    risk_level = prediction.get("risk_level", "?").upper()
    risk_score = prediction.get("risk_score", 0)
    confidence = prediction.get("confidence", 0) * 100  # Convertir en %
    
    # Emoji selon le niveau
    emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}.get(risk_level, "⚪")
    
    print(f"    {emoji} Risque: {risk_level} (Score: {risk_score:.1f}/100, Confiance: {confidence:.0f}%)")
    
    # Facteurs de risque AVEC POURCENTAGES
    factors = result.get("risk_factors", [])
    if factors:
        print("    📊 Facteurs de risque détectés:")
        for f in factors[:5]:  # Afficher jusqu'à 5 facteurs
            status_emoji = {"critical": "🔴", "warning": "🟠", "info": "🟡"}.get(f.get('status'), "⚪")
            contrib = f.get('contribution_percent', 0)
            factor_name = f.get('factor', '?')
            value = f.get('value', '?')
            message = f.get('message', '')
            print(f"       {status_emoji} {factor_name}: {value} → {contrib:.1f}% du risque")
            print(f"          └─ {message}")
    else:
        print("    ✅ Aucun facteur de risque significatif détecté")
    
    # Recommandations
    recommendations = result.get("recommendations", {})
    
    immediate = recommendations.get("immediate", [])
    if immediate:
        print("    🚨 Actions immédiates:")
        for r in immediate[:2]:
            print(f"       - {r}")
    
    preventive = recommendations.get("preventive", [])
    if preventive:
        print("    💊 Prévention:")
        for r in preventive[:2]:
            print(f"       - {r}")
    
    environmental = recommendations.get("environmental", [])
    if environmental:
        print("    🌍 Environnement:")
        for r in environmental[:3]:
            print(f"       - {r}")


def main():
    print("=" * 70)
    print("🧪 TEST RESPIRIA AI - TOUS LES PROFILS ET SCÉNARIOS")
    print("=" * 70)
    
    for scenario in SCENARIOS:
        print(f"\n{'='*70}")
        print(f"📋 SCÉNARIO: {scenario['name']}")
        print(f"{'='*70}")
        
        # Afficher les données du scénario
        data = scenario["data"]
        print(f"   Données capteurs:")
        print(f"   SpO2={data['spo2']}% | BPM={data['heart_rate']} | Resp={data['respiratory_rate']}/min")
        print(f"   Temp={data['temperature']}°C | Humid={data['humidity']}% | AQI={data['aqi']}")
        print(f"   eCO2={data['eco2']}ppm | TVOC={data['tvoc']}ppb | Pollen={data['pollen_level']}/5")
        print(f"   Médicament={'✅' if data['medication_taken'] else '❌'} | Fumée={'🚨 OUI' if data['smoke_detected'] else '✅ Non'}")
        
        print()
        
        # Tester chaque profil
        for profile_id, profile_name in PROFILES.items():
            print(f"\n  👤 Profil {profile_id}: {profile_name}")
            result = test_profile(profile_id, scenario)
            print_result(result, profile_name)
    
    print("\n" + "=" * 70)
    print("✅ TESTS TERMINÉS")
    print("=" * 70)


if __name__ == "__main__":
    main()
