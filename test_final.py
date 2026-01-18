#!/usr/bin/env python3
"""
TEST FINAL - RESPIRIA AI OPTIMISÉ
=================================

Teste toutes les fonctionnalités du système optimisé
"""

from api.respiria_ai_predictor import RespiriaAIPredictor
import json
import time

def test_all_optimizations():
    """Test complet de toutes les optimisations"""
    print("🏆 TEST FINAL - RESPIRIA AI OPTIMISÉ")
    print("=" * 60)
    print("🎯 Objectif: Valider toutes les améliorations")
    print("📅 Date:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Initialisation
    print("🧠 Initialisation du moteur IA RESPIRIA optimisé...")
    predictor = RespiriaAIPredictor()
    print("✅ Moteur IA RESPIRIA prêt\n")
    
    # Test avec un cas complexe
    test_data = {
        "profile_id": 2,  # Asthmatique sévère
        "spo2": 87.0,     # Critique
        "heart_rate": 115, # Élevé
        "respiratory_rate": 32,  # Critique
        "temperature": 5.0,  # Froid extrême
        "humidity": 85.0,    # Haute
        "aqi": 180.0,        # Dangereuse
        "pollen_level": 5,   # Maximum
        "smoke_detected": True,  # Urgence
        "medication_taken": False  # Non pris
    }
    
    print("🧪 TEST AVEC CAS COMPLEXE (Asthmatique sévère)")
    print("=" * 50)
    print("📊 Données d'entrée:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    print()
    
    # Mesure de performance
    start_time = time.time()
    result = predictor.predict(test_data)
    end_time = time.time()
    
    prediction_time = (end_time - start_time) * 1000
    
    if result['success']:
        prediction = result['prediction']
        risk_factors = result['risk_factors']
        recommendations = result['recommendations']
        metadata = result['metadata']
        
        print("🎯 RÉSULTATS DE PRÉDICTION")
        print("=" * 50)
        print(f"   Score de risque: {prediction['risk_score']}%")
        print(f"   Niveau: {prediction['risk_level'].upper()}")
        print(f"   Confiance: {prediction['confidence']:.1%}")
        print(f"   Notification: {'OUI' if prediction['should_notify'] else 'NON'}")
        print(f"   ⏱️  Temps de calcul: {prediction_time:.1f}ms")
        
        # Performance interne
        performance = metadata.get('performance', {})
        print(f"   📈 Facteurs analysés: {performance.get('factors_analyzed', 0)}")
        print(f"   💡 Recommandations générées: {performance.get('recommendations_generated', 0)}")
        print(f"   💾 Cache utilisé: {performance.get('cache_hits', 0)} hits")
        
        print(f"   📱 Modèle: {metadata.get('model')}")
        print(f"   🔢 Version: {metadata.get('version')}")
        
        print("\n🚨 FACTEURS DE RISQUE DÉTECTÉS")
        print("=" * 50)
        
        critical_factors = []
        warning_factors = []
        info_factors = []
        
        for rf in risk_factors:
            factor_info = f"   • {rf['factor']}: {rf['value']} ({rf['contribution_percent']}%)"
            
            if rf['status'] == 'critical':
                critical_factors.append(factor_info)
            elif rf['status'] == 'warning':
                warning_factors.append(factor_info)
            else:
                info_factors.append(factor_info)
        
        if critical_factors:
            print("🚨 FACTEURS CRITIQUES:")
            for factor in critical_factors:
                print(factor)
        
        if warning_factors:
            print("\n⚠️ FACTEURS D'ALERTE:")
            for factor in warning_factors:
                print(factor)
        
        if info_factors:
            print("\n💡 FACTEURS À SURVEILLER:")
            for factor in info_factors:
                print(factor)
        
        print("\n💡 RECOMMANDATIONS DÉTAILLÉES")
        print("=" * 50)
        
        if recommendations['immediate']:
            print("🚨 ACTIONS IMMÉDIATES:")
            for i, rec in enumerate(recommendations['immediate'], 1):
                print(f"   {i}. {rec}")
        
        if recommendations['preventive']:
            print("\n🛡️ ACTIONS PRÉVENTIVES:")
            for i, rec in enumerate(recommendations['preventive'], 1):
                print(f"   {i}. {rec}")
        
        if recommendations['environmental']:
            print("\n🌍 CONSEILS ENVIRONNEMENTAUX:")
            for i, rec in enumerate(recommendations['environmental'], 1):
                print(f"   {i}. {rec}")
        
        # Évaluation de la performance
        print("\n🏆 ÉVALUATION DES OPTIMISATIONS")
        print("=" * 50)
        
        if prediction_time < 10:
            print("✅ VITESSE: EXCELLENTE (< 10ms)")
        elif prediction_time < 50:
            print("✅ VITESSE: BONNE (< 50ms)")
        else:
            print("⚠️ VITESSE: À OPTIMISER")
        
        if prediction['confidence'] > 0.9:
            print("✅ CONFIANCE: ÉLEVÉE (> 90%)")
        elif prediction['confidence'] > 0.8:
            print("✅ CONFIANCE: BONNE (> 80%)")
        else:
            print("⚠️ CONFIANCE: MOYENNE")
        
        total_recommendations = sum(len(r) for r in recommendations.values())
        if total_recommendations >= 5:
            print("✅ RECOMMANDATIONS: COMPLÈTES")
        else:
            print("⚠️ RECOMMANDATIONS: LIMITÉES")
        
        factors_coverage = len(risk_factors)
        if factors_coverage >= 4:
            print("✅ ANALYSE: COMPLÈTE")
        else:
            print("⚠️ ANALYSE: PARTIELLE")
        
        print(f"\n📊 SCORE GLOBAL DES OPTIMISATIONS:")
        optimizations_score = 0
        
        if prediction_time < 10:
            optimizations_score += 25
        elif prediction_time < 50:
            optimizations_score += 20
        
        if prediction['confidence'] > 0.9:
            optimizations_score += 25
        elif prediction['confidence'] > 0.8:
            optimizations_score += 20
        
        if total_recommendations >= 5:
            optimizations_score += 25
        
        if factors_coverage >= 4:
            optimizations_score += 25
        
        print(f"   🎯 Score: {optimizations_score}/100")
        
        if optimizations_score >= 90:
            print("   🏆 EXCELLENT - Optimisations réussies")
        elif optimizations_score >= 75:
            print("   ✅ BON - Optimisations efficaces")
        elif optimizations_score >= 60:
            print("   ⚠️ MOYEN - Quelques améliorations possibles")
        else:
            print("   ❌ FAIBLE - Optimisations à revoir")
    
    else:
        print("❌ ERREUR:", result.get('error'))
    
    print("\n🎉 TEST FINAL TERMINÉ")

if __name__ == "__main__":
    test_all_optimizations()