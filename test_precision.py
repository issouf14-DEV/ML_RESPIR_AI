#!/usr/bin/env python3
"""
TEST DE PRÉCISION MÉDICALE - RESPIRIA AI
==========================================

Évalue la précision du modèle et propose des améliorations
pour atteindre le standard médical de 75-80%
"""

from api.respiria_ai_predictor import RespiriaAIPredictor
import json

def test_medical_precision():
    """Test complet de précision médicale"""
    print("🏥 ÉVALUATION DE PRÉCISION MÉDICALE - RESPIRIA AI")
    print("=" * 60)
    print("📊 Objectif: Atteindre 75-80% de précision (standard médical)")
    print()
    
    predictor = RespiriaAIPredictor()
    
    # Scénarios médicaux étendus avec résultats attendus
    scenarios = [
        {
            "name": "URGENCE ABSOLUE - SpO2 critique",
            "data": {
                "profile_id": 2, "spo2": 82.0, "heart_rate": 125, 
                "respiratory_rate": 38, "temperature": 25.0, "humidity": 60.0,
                "aqi": 50.0, "pollen_level": 1, "smoke_detected": False, "medication_taken": True
            },
            "expected": {"risk_level": "high", "should_notify": True, "min_score": 80}
        },
        {
            "name": "SITUATION NORMALE - Personne saine",
            "data": {
                "profile_id": 1, "spo2": 98.0, "heart_rate": 70, 
                "respiratory_rate": 16, "temperature": 22.0, "humidity": 50.0,
                "aqi": 40.0, "pollen_level": 1, "smoke_detected": False, "medication_taken": True
            },
            "expected": {"risk_level": "low", "should_notify": False, "max_score": 15}
        },
        {
            "name": "URGENCE FUMÉE - Évacuation",
            "data": {
                "profile_id": 1, "spo2": 94.0, "heart_rate": 85, 
                "respiratory_rate": 20, "temperature": 25.0, "humidity": 55.0,
                "aqi": 80.0, "pollen_level": 2, "smoke_detected": True, "medication_taken": True
            },
            "expected": {"risk_level": "high", "should_notify": True, "min_score": 50}
        },
        {
            "name": "CAS LIMITE - SpO2 92%",
            "data": {
                "profile_id": 1, "spo2": 92.0, "heart_rate": 80, 
                "respiratory_rate": 18, "temperature": 20.0, "humidity": 45.0,
                "aqi": 60.0, "pollen_level": 2, "smoke_detected": False, "medication_taken": True
            },
            "expected": {"risk_level": "medium", "should_notify": False, "max_score": 50}
        },
        {
            "name": "ASTHMATIQUE SÉVÈRE - Stable",
            "data": {
                "profile_id": 2, "spo2": 95.0, "heart_rate": 75, 
                "respiratory_rate": 18, "temperature": 24.0, "humidity": 55.0,
                "aqi": 70.0, "pollen_level": 3, "smoke_detected": False, "medication_taken": True
            },
            "expected": {"risk_level": "medium", "should_notify": False, "max_score": 40}
        },
        {
            "name": "QUALITÉ AIR MOYENNE",
            "data": {
                "profile_id": 1, "spo2": 96.0, "heart_rate": 72, 
                "respiratory_rate": 17, "temperature": 28.0, "humidity": 65.0,
                "aqi": 120.0, "pollen_level": 3, "smoke_detected": False, "medication_taken": True
            },
            "expected": {"risk_level": "medium", "should_notify": False, "max_score": 45}
        },
        {
            "name": "DÉTRESSE RESPIRATOIRE",
            "data": {
                "profile_id": 2, "spo2": 89.0, "heart_rate": 115, 
                "respiratory_rate": 32, "temperature": 22.0, "humidity": 50.0,
                "aqi": 90.0, "pollen_level": 2, "smoke_detected": False, "medication_taken": False
            },
            "expected": {"risk_level": "high", "should_notify": True, "min_score": 75}
        },
        {
            "name": "PRÉVENTION - Légère exposition",
            "data": {
                "profile_id": 1, "spo2": 97.0, "heart_rate": 78, 
                "respiratory_rate": 19, "temperature": 30.0, "humidity": 75.0,
                "aqi": 90.0, "pollen_level": 4, "smoke_detected": False, "medication_taken": True
            },
            "expected": {"risk_level": "medium", "should_notify": False, "max_score": 40}  # Corrigé: pollen 4 + AQI 90 = medium
        }
    ]
    
    correct_predictions = 0
    total_tests = len(scenarios)
    detailed_results = []
    
    print("🧪 TESTS DE PRÉCISION")
    print("=" * 40)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🧪 TEST {i}: {scenario['name']}")
        print("-" * 45)
        
        result = predictor.predict(scenario['data'])
        
        if result['success']:
            prediction = result['prediction']
            expected = scenario['expected']
            
            # Vérifications
            checks = {
                'risk_level': prediction['risk_level'] == expected['risk_level'],
                'notification': prediction['should_notify'] == expected['should_notify'],
                'score_range': True
            }
            
            # Vérifier plage de score
            score = prediction['risk_score']
            if 'min_score' in expected:
                checks['score_range'] = score >= expected['min_score']
            if 'max_score' in expected:
                checks['score_range'] = score <= expected['max_score']
            
            # Compter succès
            if all(checks.values()):
                correct_predictions += 1
                status = "✅ RÉUSSI"
            else:
                status = "❌ ÉCHOUÉ"
            
            print(f"📊 Résultat: {status}")
            print(f"   Score: {score}% (attendu: {expected.get('min_score', 0)}-{expected.get('max_score', 100)}%)")
            print(f"   Niveau: {prediction['risk_level']} (attendu: {expected['risk_level']})")
            print(f"   Notification: {prediction['should_notify']} (attendu: {expected['should_notify']})")
            print(f"   Confiance: {prediction['confidence']:.1%}")
            
            # Détails des erreurs
            errors = []
            if not checks['risk_level']:
                errors.append(f"Niveau incorrect: {prediction['risk_level']} vs {expected['risk_level']}")
            if not checks['notification']:
                errors.append(f"Notification incorrecte: {prediction['should_notify']} vs {expected['should_notify']}")
            if not checks['score_range']:
                errors.append(f"Score hors plage: {score}%")
            
            if errors:
                print(f"   ⚠️ Erreurs: {', '.join(errors)}")
            
            detailed_results.append({
                'scenario': scenario['name'],
                'success': all(checks.values()),
                'score': score,
                'level': prediction['risk_level'],
                'notify': prediction['should_notify'],
                'errors': errors
            })
        
        else:
            print(f"❌ ERREUR: {result.get('error')}")
    
    # Calcul de la précision
    precision = (correct_predictions / total_tests) * 100
    
    print(f"\n🏆 RÉSULTATS GLOBAUX")
    print("=" * 40)
    print(f"Tests réussis: {correct_predictions}/{total_tests}")
    print(f"Précision actuelle: {precision:.1f}%")
    print()
    
    # Évaluation selon standards médicaux
    print("📊 ÉVALUATION SELON STANDARDS MÉDICAUX")
    print("=" * 40)
    
    if precision >= 80:
        print("🏆 EXCELLENT - Dépasse le standard médical (≥80%)")
        recommendation = "Modèle prêt pour production"
    elif precision >= 75:
        print("✅ BON - Atteint le standard médical (75-80%)")
        recommendation = "Modèle acceptable pour usage clinique"
    elif precision >= 60:
        print("⚠️ MOYEN - En dessous du standard (60-75%)")
        recommendation = "Calibrations nécessaires avant usage clinique"
    else:
        print("❌ FAIBLE - Insuffisant pour usage médical (<60%)")
        recommendation = "Révision complète du modèle requise"
    
    print(f"💡 Recommandation: {recommendation}")
    
    # Analyse détaillée des échecs
    failed_scenarios = [r for r in detailed_results if not r['success']]
    if failed_scenarios:
        print(f"\n🔍 ANALYSE DES ÉCHECS ({len(failed_scenarios)} cas)")
        print("=" * 40)
        
        for fail in failed_scenarios:
            print(f"❌ {fail['scenario']}")
            for error in fail['errors']:
                print(f"   → {error}")
    
    # Recommandations d'amélioration
    print(f"\n🔧 RECOMMANDATIONS D'AMÉLIORATION")
    print("=" * 40)
    
    if precision < 75:
        print("Pour atteindre le standard médical de 75-80%:")
        print("1. 🎯 Ajuster les seuils de classification")
        print("2. 🧠 Améliorer la logique de notification")
        print("3. 🔍 Ajouter validation croisée des indicateurs")
        print("4. 📊 Recalibrer les scores par profil utilisateur")
        print("5. 🏥 Valider avec plus de cas cliniques réels")
    
    return precision, detailed_results

if __name__ == "__main__":
    precision, results = test_medical_precision()
    
    print(f"\n🎯 CONCLUSION")
    print("=" * 40)
    print(f"Précision actuelle: {precision:.1f}%")
    print(f"Standard requis: 75-80%")
    
    if precision >= 75:
        print("✅ MODÈLE CONFORME aux standards médicaux")
    else:
        gap = 75 - precision
        print(f"❌ ÉCART: {gap:.1f} points à combler pour conformité")
        print("🔧 Améliorations nécessaires avant production")