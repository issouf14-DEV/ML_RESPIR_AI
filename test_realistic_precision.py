#!/usr/bin/env python3
"""
TEST DE PRÉCISION RÉALISTE - RESPIRIA AI
==========================================
50+ scénarios variés pour une évaluation réaliste
Inclut des cas limites et ambigus
"""

import random
from api.respiria_ai_predictor import RespiriaAIPredictor

def generate_realistic_scenarios():
    """Génère 50+ scénarios réalistes et variés"""
    
    scenarios = []
    
    # ============================================
    # GROUPE 1: URGENCES ÉVIDENTES (10 cas)
    # ============================================
    
    # SpO2 critique
    scenarios.append({
        "name": "SpO2 critique 82%",
        "data": {"profile_id": 2, "spo2": 82, "heart_rate": 120, "respiratory_rate": 35,
                 "temperature": 25, "humidity": 60, "aqi": 50, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "high"
    })
    
    scenarios.append({
        "name": "SpO2 très critique 78%",
        "data": {"profile_id": 2, "spo2": 78, "heart_rate": 130, "respiratory_rate": 40,
                 "temperature": 22, "humidity": 55, "aqi": 60, "pollen_level": 1,
                 "smoke_detected": False, "medication_taken": False},
        "expected_level": "high"
    })
    
    # Fumée détectée
    scenarios.append({
        "name": "Fumée avec SpO2 normal",
        "data": {"profile_id": 1, "spo2": 97, "heart_rate": 75, "respiratory_rate": 16,
                 "temperature": 25, "humidity": 50, "aqi": 40, "pollen_level": 1,
                 "smoke_detected": True, "medication_taken": True},
        "expected_level": "high"
    })
    
    scenarios.append({
        "name": "Fumée avec asthmatique sévère",
        "data": {"profile_id": 2, "spo2": 94, "heart_rate": 90, "respiratory_rate": 22,
                 "temperature": 28, "humidity": 65, "aqi": 100, "pollen_level": 3,
                 "smoke_detected": True, "medication_taken": True},
        "expected_level": "high"
    })
    
    # Détresse respiratoire
    scenarios.append({
        "name": "Détresse respiratoire sévère",
        "data": {"profile_id": 2, "spo2": 88, "heart_rate": 125, "respiratory_rate": 38,
                 "temperature": 30, "humidity": 70, "aqi": 120, "pollen_level": 4,
                 "smoke_detected": False, "medication_taken": False},
        "expected_level": "high"
    })
    
    scenarios.append({
        "name": "SpO2 85% + tachycardie",
        "data": {"profile_id": 1, "spo2": 85, "heart_rate": 135, "respiratory_rate": 32,
                 "temperature": 25, "humidity": 55, "aqi": 80, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "high"
    })
    
    # Combinaison facteurs critiques
    scenarios.append({
        "name": "Multi-facteurs critiques",
        "data": {"profile_id": 2, "spo2": 86, "heart_rate": 140, "respiratory_rate": 36,
                 "temperature": 38, "humidity": 90, "aqi": 250, "pollen_level": 5,
                 "smoke_detected": False, "medication_taken": False},
        "expected_level": "high"
    })
    
    scenarios.append({
        "name": "AQI dangereux + SpO2 bas",
        "data": {"profile_id": 2, "spo2": 87, "heart_rate": 115, "respiratory_rate": 30,
                 "temperature": 32, "humidity": 75, "aqi": 300, "pollen_level": 4,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "high"
    })
    
    scenarios.append({
        "name": "Crise asthmatique aiguë",
        "data": {"profile_id": 2, "spo2": 84, "heart_rate": 145, "respiratory_rate": 42,
                 "temperature": 25, "humidity": 60, "aqi": 100, "pollen_level": 3,
                 "smoke_detected": False, "medication_taken": False},
        "expected_level": "high"
    })
    
    scenarios.append({
        "name": "Urgence environnementale totale",
        "data": {"profile_id": 2, "spo2": 89, "heart_rate": 120, "respiratory_rate": 28,
                 "temperature": 5, "humidity": 95, "aqi": 350, "pollen_level": 5,
                 "smoke_detected": True, "medication_taken": False},
        "expected_level": "high"
    })
    
    # ============================================
    # GROUPE 2: SITUATIONS NORMALES (10 cas)
    # ============================================
    
    scenarios.append({
        "name": "Personne saine parfaite",
        "data": {"profile_id": 0, "spo2": 99, "heart_rate": 68, "respiratory_rate": 14,
                 "temperature": 22, "humidity": 50, "aqi": 25, "pollen_level": 1,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "low"
    })
    
    scenarios.append({
        "name": "Asthmatique stable contrôlé",
        "data": {"profile_id": 1, "spo2": 97, "heart_rate": 72, "respiratory_rate": 15,
                 "temperature": 21, "humidity": 45, "aqi": 35, "pollen_level": 1,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "low"
    })
    
    scenarios.append({
        "name": "Rémission avec bonnes conditions",
        "data": {"profile_id": 3, "spo2": 98, "heart_rate": 65, "respiratory_rate": 14,
                 "temperature": 23, "humidity": 55, "aqi": 30, "pollen_level": 1,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "low"
    })
    
    scenarios.append({
        "name": "Jeune sportif en forme",
        "data": {"profile_id": 0, "spo2": 99, "heart_rate": 55, "respiratory_rate": 12,
                 "temperature": 20, "humidity": 40, "aqi": 20, "pollen_level": 1,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "low"
    })
    
    scenarios.append({
        "name": "Conditions environnementales idéales",
        "data": {"profile_id": 1, "spo2": 98, "heart_rate": 70, "respiratory_rate": 16,
                 "temperature": 22, "humidity": 50, "aqi": 15, "pollen_level": 1,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "low"
    })
    
    scenarios.append({
        "name": "Personne âgée stable",
        "data": {"profile_id": 1, "spo2": 96, "heart_rate": 75, "respiratory_rate": 17,
                 "temperature": 23, "humidity": 52, "aqi": 40, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "low"
    })
    
    scenarios.append({
        "name": "Enfant asthmatique contrôlé",
        "data": {"profile_id": 1, "spo2": 98, "heart_rate": 85, "respiratory_rate": 18,
                 "temperature": 21, "humidity": 48, "aqi": 35, "pollen_level": 1,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "low"
    })
    
    scenarios.append({
        "name": "Prévention routine",
        "data": {"profile_id": 0, "spo2": 98, "heart_rate": 70, "respiratory_rate": 15,
                 "temperature": 24, "humidity": 55, "aqi": 45, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "low"
    })
    
    scenarios.append({
        "name": "Matin calme",
        "data": {"profile_id": 1, "spo2": 97, "heart_rate": 65, "respiratory_rate": 14,
                 "temperature": 20, "humidity": 45, "aqi": 30, "pollen_level": 1,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "low"
    })
    
    scenarios.append({
        "name": "Soirée tranquille",
        "data": {"profile_id": 0, "spo2": 98, "heart_rate": 68, "respiratory_rate": 15,
                 "temperature": 22, "humidity": 50, "aqi": 35, "pollen_level": 1,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "low"
    })
    
    # ============================================
    # GROUPE 3: SITUATIONS MOYENNES (15 cas)
    # ============================================
    
    scenarios.append({
        "name": "SpO2 limite 92%",
        "data": {"profile_id": 1, "spo2": 92, "heart_rate": 85, "respiratory_rate": 20,
                 "temperature": 26, "humidity": 65, "aqi": 80, "pollen_level": 3,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium"
    })
    
    scenarios.append({
        "name": "AQI modéré élevé",
        "data": {"profile_id": 1, "spo2": 95, "heart_rate": 78, "respiratory_rate": 18,
                 "temperature": 28, "humidity": 70, "aqi": 130, "pollen_level": 3,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium"
    })
    
    scenarios.append({
        "name": "Pollen élevé",
        "data": {"profile_id": 1, "spo2": 96, "heart_rate": 80, "respiratory_rate": 19,
                 "temperature": 25, "humidity": 60, "aqi": 70, "pollen_level": 4,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium"
    })
    
    scenarios.append({
        "name": "Asthmatique sévère stable",
        "data": {"profile_id": 2, "spo2": 94, "heart_rate": 82, "respiratory_rate": 19,
                 "temperature": 24, "humidity": 55, "aqi": 60, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium"
    })
    
    scenarios.append({
        "name": "Médicament non pris",
        "data": {"profile_id": 1, "spo2": 95, "heart_rate": 80, "respiratory_rate": 18,
                 "temperature": 23, "humidity": 55, "aqi": 50, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": False},
        "expected_level": "medium"
    })
    
    scenarios.append({
        "name": "Chaleur extrême",
        "data": {"profile_id": 1, "spo2": 96, "heart_rate": 90, "respiratory_rate": 20,
                 "temperature": 38, "humidity": 75, "aqi": 80, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium"
    })
    
    scenarios.append({
        "name": "Froid extrême",
        "data": {"profile_id": 1, "spo2": 95, "heart_rate": 75, "respiratory_rate": 18,
                 "temperature": 2, "humidity": 40, "aqi": 50, "pollen_level": 1,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium"
    })
    
    scenarios.append({
        "name": "Humidité excessive",
        "data": {"profile_id": 1, "spo2": 95, "heart_rate": 82, "respiratory_rate": 19,
                 "temperature": 30, "humidity": 90, "aqi": 70, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium"
    })
    
    scenarios.append({
        "name": "Tachycardie légère",
        "data": {"profile_id": 1, "spo2": 96, "heart_rate": 105, "respiratory_rate": 20,
                 "temperature": 25, "humidity": 55, "aqi": 60, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium"
    })
    
    scenarios.append({
        "name": "Respiration rapide",
        "data": {"profile_id": 1, "spo2": 95, "heart_rate": 85, "respiratory_rate": 24,
                 "temperature": 26, "humidity": 60, "aqi": 70, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium"
    })
    
    scenarios.append({
        "name": "Combinaison stress modéré",
        "data": {"profile_id": 1, "spo2": 94, "heart_rate": 95, "respiratory_rate": 22,
                 "temperature": 28, "humidity": 70, "aqi": 100, "pollen_level": 3,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium"
    })
    
    scenarios.append({
        "name": "Après effort physique",
        "data": {"profile_id": 1, "spo2": 94, "heart_rate": 110, "respiratory_rate": 25,
                 "temperature": 22, "humidity": 50, "aqi": 40, "pollen_level": 1,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium"
    })
    
    scenarios.append({
        "name": "Allergie saisonnière",
        "data": {"profile_id": 1, "spo2": 95, "heart_rate": 80, "respiratory_rate": 19,
                 "temperature": 25, "humidity": 55, "aqi": 60, "pollen_level": 5,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium"
    })
    
    scenarios.append({
        "name": "Pollution urbaine",
        "data": {"profile_id": 1, "spo2": 95, "heart_rate": 78, "respiratory_rate": 18,
                 "temperature": 25, "humidity": 50, "aqi": 140, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium"
    })
    
    scenarios.append({
        "name": "Sévère sans traitement",
        "data": {"profile_id": 2, "spo2": 93, "heart_rate": 88, "respiratory_rate": 21,
                 "temperature": 25, "humidity": 60, "aqi": 80, "pollen_level": 3,
                 "smoke_detected": False, "medication_taken": False},
        "expected_level": "medium"
    })
    
    # ============================================
    # GROUPE 4: CAS LIMITES AMBIGUS (15 cas)
    # Ces cas sont difficiles à classifier
    # ============================================
    
    scenarios.append({
        "name": "AMBIGU: SpO2 90% exactement",
        "data": {"profile_id": 1, "spo2": 90, "heart_rate": 85, "respiratory_rate": 20,
                 "temperature": 25, "humidity": 55, "aqi": 60, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium",  # Pourrait être high
        "ambiguous": True
    })
    
    scenarios.append({
        "name": "AMBIGU: Frontière low/medium",
        "data": {"profile_id": 1, "spo2": 96, "heart_rate": 78, "respiratory_rate": 17,
                 "temperature": 26, "humidity": 62, "aqi": 55, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "low",  # Pourrait être medium
        "ambiguous": True
    })
    
    scenarios.append({
        "name": "AMBIGU: Sévère en bonnes conditions",
        "data": {"profile_id": 2, "spo2": 96, "heart_rate": 75, "respiratory_rate": 16,
                 "temperature": 22, "humidity": 50, "aqi": 40, "pollen_level": 1,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "low",  # Sévère mais tout est bon
        "ambiguous": True
    })
    
    scenarios.append({
        "name": "AMBIGU: Prévention en mauvais environnement",
        "data": {"profile_id": 0, "spo2": 97, "heart_rate": 75, "respiratory_rate": 17,
                 "temperature": 35, "humidity": 85, "aqi": 180, "pollen_level": 5,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium",
        "ambiguous": True
    })
    
    scenarios.append({
        "name": "AMBIGU: SpO2 89% limite haute",
        "data": {"profile_id": 1, "spo2": 89, "heart_rate": 90, "respiratory_rate": 22,
                 "temperature": 25, "humidity": 60, "aqi": 70, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "high",  # 89% devrait être high
        "ambiguous": True
    })
    
    scenarios.append({
        "name": "AMBIGU: Tout moyen sauf fumée",
        "data": {"profile_id": 1, "spo2": 95, "heart_rate": 80, "respiratory_rate": 18,
                 "temperature": 25, "humidity": 55, "aqi": 50, "pollen_level": 2,
                 "smoke_detected": True, "medication_taken": True},
        "expected_level": "high",  # Fumée = toujours high
        "ambiguous": False
    })
    
    scenarios.append({
        "name": "AMBIGU: Rémission avec pollen max",
        "data": {"profile_id": 3, "spo2": 96, "heart_rate": 78, "respiratory_rate": 18,
                 "temperature": 28, "humidity": 65, "aqi": 80, "pollen_level": 5,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium",
        "ambiguous": True
    })
    
    scenarios.append({
        "name": "AMBIGU: SpO2 91% avec bon environnement",
        "data": {"profile_id": 1, "spo2": 91, "heart_rate": 80, "respiratory_rate": 19,
                 "temperature": 22, "humidity": 50, "aqi": 30, "pollen_level": 1,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium",
        "ambiguous": True
    })
    
    scenarios.append({
        "name": "AMBIGU: Tout limite supérieur medium",
        "data": {"profile_id": 1, "spo2": 93, "heart_rate": 98, "respiratory_rate": 23,
                 "temperature": 30, "humidity": 75, "aqi": 130, "pollen_level": 4,
                 "smoke_detected": False, "medication_taken": False},
        "expected_level": "medium",  # Pourrait être high
        "ambiguous": True
    })
    
    scenarios.append({
        "name": "AMBIGU: Sévère avec un seul facteur",
        "data": {"profile_id": 2, "spo2": 95, "heart_rate": 78, "respiratory_rate": 17,
                 "temperature": 25, "humidity": 55, "aqi": 200, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium",
        "ambiguous": True
    })
    
    scenarios.append({
        "name": "AMBIGU: Effort + chaleur",
        "data": {"profile_id": 1, "spo2": 94, "heart_rate": 115, "respiratory_rate": 26,
                 "temperature": 35, "humidity": 70, "aqi": 60, "pollen_level": 2,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium",
        "ambiguous": True
    })
    
    scenarios.append({
        "name": "AMBIGU: Nuit froide",
        "data": {"profile_id": 1, "spo2": 95, "heart_rate": 68, "respiratory_rate": 16,
                 "temperature": -2, "humidity": 35, "aqi": 40, "pollen_level": 1,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium",
        "ambiguous": True
    })
    
    scenarios.append({
        "name": "AMBIGU: SpO2 94% sévère",
        "data": {"profile_id": 2, "spo2": 94, "heart_rate": 85, "respiratory_rate": 20,
                 "temperature": 26, "humidity": 60, "aqi": 90, "pollen_level": 3,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium",
        "ambiguous": True
    })
    
    scenarios.append({
        "name": "AMBIGU: Multiple facteurs légers",
        "data": {"profile_id": 1, "spo2": 95, "heart_rate": 88, "respiratory_rate": 20,
                 "temperature": 29, "humidity": 68, "aqi": 85, "pollen_level": 3,
                 "smoke_detected": False, "medication_taken": False},
        "expected_level": "medium",
        "ambiguous": True
    })
    
    scenarios.append({
        "name": "AMBIGU: Prévention avec AQI max",
        "data": {"profile_id": 0, "spo2": 98, "heart_rate": 72, "respiratory_rate": 16,
                 "temperature": 25, "humidity": 55, "aqi": 400, "pollen_level": 1,
                 "smoke_detected": False, "medication_taken": True},
        "expected_level": "medium",
        "ambiguous": True
    })
    
    return scenarios


def run_realistic_test():
    """Exécute le test réaliste"""
    print("🏥 TEST DE PRÉCISION RÉALISTE - RESPIRIA AI")
    print("=" * 60)
    print("🎯 Objectif: Évaluation réaliste avec 50+ scénarios")
    print("⚠️  Inclut des cas limites et ambigus")
    print()
    
    predictor = RespiriaAIPredictor()
    scenarios = generate_realistic_scenarios()
    
    # Compteurs
    total = len(scenarios)
    correct = 0
    correct_strict = 0
    ambiguous_correct = 0
    ambiguous_total = 0
    
    # Par catégorie
    results_by_expected = {"low": [], "medium": [], "high": []}
    errors = []
    
    print(f"📊 Total scénarios: {total}")
    print("-" * 60)
    
    for i, scenario in enumerate(scenarios, 1):
        result = predictor.predict(scenario["data"])
        
        if not result.get("success"):
            errors.append(f"Erreur: {scenario['name']}")
            continue
        
        predicted = result["prediction"]["risk_level"]
        expected = scenario["expected_level"]
        is_ambiguous = scenario.get("ambiguous", False)
        
        is_correct = predicted == expected
        
        if is_correct:
            correct += 1
            if not is_ambiguous:
                correct_strict += 1
        
        if is_ambiguous:
            ambiguous_total += 1
            if is_correct:
                ambiguous_correct += 1
        
        # Stocker résultat
        results_by_expected[expected].append({
            "name": scenario["name"],
            "predicted": predicted,
            "correct": is_correct,
            "ambiguous": is_ambiguous,
            "score": result["prediction"]["risk_score"]
        })
        
        # Afficher les erreurs
        if not is_correct:
            amb_tag = " [AMBIGU]" if is_ambiguous else ""
            errors.append(f"❌ {scenario['name']}{amb_tag}: prédit {predicted}, attendu {expected}")
    
    # Calculs
    precision = (correct / total) * 100
    non_ambiguous = total - ambiguous_total
    strict_precision = (correct_strict / non_ambiguous) * 100 if non_ambiguous > 0 else 0
    
    # Affichage résultats
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DÉTAILLÉS")
    print("=" * 60)
    
    for level in ["low", "medium", "high"]:
        results = results_by_expected[level]
        if results:
            level_correct = sum(1 for r in results if r["correct"])
            level_total = len(results)
            level_pct = (level_correct / level_total) * 100
            print(f"\n{level.upper()} ({level_total} cas):")
            print(f"   Corrects: {level_correct}/{level_total} ({level_pct:.1f}%)")
    
    print("\n" + "=" * 60)
    print("🎯 PRÉCISION GLOBALE")
    print("=" * 60)
    
    print(f"\n📊 RÉSULTATS:")
    print(f"   Total scénarios: {total}")
    print(f"   Prédictions correctes: {correct}")
    print(f"   Cas ambigus: {ambiguous_total}")
    print()
    print(f"🎯 PRÉCISION GLOBALE: {precision:.1f}%")
    print(f"🎯 PRÉCISION (hors ambigus): {strict_precision:.1f}%")
    print(f"🎯 Précision sur cas ambigus: {ambiguous_correct}/{ambiguous_total} ({(ambiguous_correct/ambiguous_total*100) if ambiguous_total > 0 else 0:.1f}%)")
    
    # Évaluation
    print("\n" + "=" * 60)
    print("📋 ÉVALUATION MÉDICALE RÉALISTE")
    print("=" * 60)
    
    if precision >= 95:
        print("⚠️  > 95% - Vérifier overfitting!")
    elif precision >= 90:
        print("🏆 90-95% - EXCELLENT pour IA médicale")
    elif precision >= 85:
        print("✅ 85-90% - TRÈS BON (standard clinique)")
    elif precision >= 80:
        print("✅ 80-85% - BON (acceptable)")
    elif precision >= 75:
        print("⚠️  75-80% - MINIMUM médical")
    else:
        print("❌ < 75% - INSUFFISANT")
    
    # Erreurs détaillées
    if errors:
        print(f"\n❌ ERREURS DÉTAILLÉES ({len(errors)}):")
        print("-" * 40)
        for err in errors[:15]:  # Max 15 erreurs affichées
            print(f"   {err}")
        if len(errors) > 15:
            print(f"   ... et {len(errors) - 15} autres erreurs")
    
    print("\n" + "=" * 60)
    print("🏆 CONCLUSION")
    print("=" * 60)
    print(f"   Précision réaliste: {precision:.1f}%")
    print(f"   Précision stricte (hors ambigus): {strict_precision:.1f}%")
    print()
    print("   📌 NOTE: Cette précision est RÉALISTE car elle inclut:")
    print("      • Cas limites difficiles")
    print("      • Situations ambiguës")
    print("      • Différents profils patients")
    print("      • Conditions environnementales variées")
    
    return precision, strict_precision


if __name__ == "__main__":
    precision, strict = run_realistic_test()
