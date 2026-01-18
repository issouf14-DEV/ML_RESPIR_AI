#!/usr/bin/env python3
"""
TEST DE PERFORMANCE - RESPIRIA AI OPTIMISÉ
==============================================

Teste les améliorations de vitesse et performance du modèle
"""

import time
import statistics
from api.respiria_ai_predictor import RespiriaAIPredictor

def test_prediction_speed():
    """Test la vitesse de prédiction"""
    print("🚀 TEST DE VITESSE DE PRÉDICTION")
    print("=" * 50)
    
    # Initialisation
    print("🧠 Initialisation du moteur IA RESPIRIA...")
    predictor = RespiriaAIPredictor()
    print("✅ Moteur IA RESPIRIA prêt\n")
    
    # Données de test variées
    test_scenarios = [
        # Scénario normal
        {
            "name": "Normal",
            "data": {
                "profile_id": 1,
                "spo2": 98.0,
                "heart_rate": 72,
                "respiratory_rate": 16,
                "temperature": 22.0,
                "humidity": 55.0,
                "aqi": 45.0,
                "pollen_level": 2,
                "smoke_detected": False,
                "medication_taken": True
            }
        },
        # Scénario critique
        {
            "name": "Critique",
            "data": {
                "profile_id": 2,
                "spo2": 85.0,
                "heart_rate": 120,
                "respiratory_rate": 35,
                "temperature": 35.0,
                "humidity": 85.0,
                "aqi": 200.0,
                "pollen_level": 5,
                "smoke_detected": True,
                "medication_taken": False
            }
        },
        # Scénario moyen
        {
            "name": "Moyen",
            "data": {
                "profile_id": 1,
                "spo2": 92.0,
                "heart_rate": 85,
                "respiratory_rate": 22,
                "temperature": 28.0,
                "humidity": 70.0,
                "aqi": 120.0,
                "pollen_level": 3,
                "smoke_detected": False,
                "medication_taken": True
            }
        }
    ]
    
    total_times = []
    
    for scenario in test_scenarios:
        print(f"📊 Test scenario: {scenario['name']}")
        print("-" * 30)
        
        times = []
        results = []
        
        # Faire 10 prédictions pour mesurer la vitesse moyenne
        for i in range(10):
            start_time = time.time()
            result = predictor.predict(scenario['data'])
            end_time = time.time()
            
            prediction_time = (end_time - start_time) * 1000  # En millisecondes
            times.append(prediction_time)
            results.append(result)
        
        # Statistiques
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        
        print(f"   ⏱️  Temps moyen: {avg_time:.1f}ms")
        print(f"   ⚡ Temps minimum: {min_time:.1f}ms")
        print(f"   🐌 Temps maximum: {max_time:.1f}ms")
        print(f"   📊 Écart-type: {std_dev:.1f}ms")
        
        # Analyser le résultat
        if results[0]['success']:
            metadata = results[0].get('metadata', {})
            internal_time = metadata.get('prediction_time_ms', 0)
            print(f"   🔧 Temps interne: {internal_time}ms")
            print(f"   🎯 Score de risque: {results[0]['prediction']['risk_score']}%")
            print(f"   🛡️  Confiance: {results[0]['prediction']['confidence']:.1%}")
            
            # Performance cache
            performance = metadata.get('performance', {})
            if performance:
                print(f"   📈 Facteurs analysés: {performance.get('factors_analyzed', 0)}")
                print(f"   💡 Recommandations: {performance.get('recommendations_generated', 0)}")
                print(f"   💾 Cache hits: {performance.get('cache_hits', 0)}")
        
        total_times.extend(times)
        print()
    
    # Statistiques globales
    print("🏆 STATISTIQUES GLOBALES")
    print("=" * 50)
    
    global_avg = statistics.mean(total_times)
    global_min = min(total_times)
    global_max = max(total_times)
    global_std = statistics.stdev(total_times)
    
    print(f"📊 Moyenne globale: {global_avg:.1f}ms")
    print(f"⚡ Plus rapide: {global_min:.1f}ms")
    print(f"🐌 Plus lent: {global_max:.1f}ms")
    print(f"📈 Écart-type: {global_std:.1f}ms")
    print(f"🎯 Nombre de tests: {len(total_times)}")
    
    # Évaluation de la performance
    print("\n💡 ÉVALUATION DE LA PERFORMANCE")
    print("=" * 50)
    
    if global_avg < 50:
        print("🚀 EXCELLENTE - Très rapide pour usage temps réel")
    elif global_avg < 100:
        print("✅ BONNE - Acceptable pour applications mobiles")
    elif global_avg < 200:
        print("⚠️ MOYENNE - Peut nécessiter des optimisations")
    else:
        print("❌ LENTE - Optimisations nécessaires")
    
    # Recommandations
    print(f"\n🎯 OBJECTIFS DE PERFORMANCE:")
    print(f"   • Mobile temps réel: < 100ms")
    print(f"   • Application web: < 200ms")
    print(f"   • Backend batch: < 500ms")
    print(f"   • Actuel: {global_avg:.1f}ms")
    
    if global_avg < 100:
        print("   ✅ OBJECTIF MOBILE ATTEINT")
    if global_avg < 200:
        print("   ✅ OBJECTIF WEB ATTEINT")

def test_cache_effectiveness():
    """Test l'efficacité du système de cache"""
    print("\n💾 TEST D'EFFICACITÉ DU CACHE")
    print("=" * 50)
    
    predictor = RespiriaAIPredictor()
    
    # Données identiques pour tester le cache
    data = {
        "profile_id": 1,
        "spo2": 95.0,
        "heart_rate": 80,
        "respiratory_rate": 18,
        "temperature": 25.0,
        "humidity": 60.0,
        "aqi": 75.0,
        "pollen_level": 2,
        "smoke_detected": False,
        "medication_taken": True
    }
    
    # Premier appel (pas de cache)
    start_time = time.time()
    result1 = predictor.predict(data)
    first_call_time = (time.time() - start_time) * 1000
    
    # Deuxième appel (avec cache potentiel)
    start_time = time.time()
    result2 = predictor.predict(data)
    second_call_time = (time.time() - start_time) * 1000
    
    print(f"🥇 Premier appel: {first_call_time:.1f}ms")
    print(f"🥈 Deuxième appel: {second_call_time:.1f}ms")
    
    if second_call_time < first_call_time * 0.8:
        improvement = ((first_call_time - second_call_time) / first_call_time) * 100
        print(f"✅ Amélioration cache: {improvement:.1f}%")
    else:
        print("❌ Cache pas détecté ou inefficace")
    
    # Vérifier la cohérence des résultats
    if (result1['prediction']['risk_score'] == result2['prediction']['risk_score'] and
        result1['prediction']['risk_level'] == result2['prediction']['risk_level']):
        print("✅ Cohérence des résultats maintenue")
    else:
        print("❌ Incohérence détectée entre les appels")

if __name__ == "__main__":
    print("🧪 TESTS DE PERFORMANCE - RESPIRIA AI")
    print("=" * 60)
    print("🎯 Objectif: Mesurer les améliorations de vitesse")
    print("📅 Date:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Test principal de vitesse
    test_prediction_speed()
    
    # Test du cache
    test_cache_effectiveness()
    
    print("\n🎉 TESTS TERMINÉS")