#!/usr/bin/env python3
"""
Script Keep-Alive pour RESPIRIA AI
Ping le serveur toutes les 5 minutes pour empêcher Render de l'endormir.

FONCTIONNALITÉS:
  - Démarre automatiquement avec Windows (si ajouté au Startup)
  - Attend la connexion internet avant de commencer
  - Réessaie automatiquement si la connexion est perdue
  - Log toutes les activités

Usage:
  python keep_alive.py                  # Mode interactif
  pythonw keep_alive.py                 # Mode silencieux (sans console)
"""

import time
import datetime
import sys
import os
import socket

try:
    import requests
except ImportError:
    print("❌ Module 'requests' non installé. Exécutez: pip install requests")
    sys.exit(1)

# Configuration
API_URL = "https://ml-respir-ai.onrender.com/health"
PING_INTERVAL = 300  # 5 minutes en secondes
INTERNET_CHECK_INTERVAL = 30  # Vérifier internet toutes les 30 secondes
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keep_alive.log")


def check_internet() -> bool:
    """Vérifie si internet est disponible."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def wait_for_internet():
    """Attend que la connexion internet soit disponible."""
    if check_internet():
        return True
    
    log_message("📡 En attente de connexion internet...", console_only=True)
    
    while not check_internet():
        time.sleep(INTERNET_CHECK_INTERVAL)
    
    log_message("✅ Connexion internet détectée!")
    return True

def log_message(message: str, to_file: bool = True, console_only: bool = False):
    """Affiche et enregistre un message avec timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    print(formatted)
    
    if to_file and not console_only:
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(formatted + "\n")
        except Exception:
            pass

def ping_server() -> bool:
    """Ping le serveur et retourne True si succès."""
    try:
        response = requests.get(API_URL, timeout=30)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            log_message(f"✅ Ping OK - Status: {status}")
            return True
        else:
            log_message(f"⚠️ Ping échoué - Code: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        log_message("⏰ Timeout - Le serveur se réveille...")
        return False
    except requests.exceptions.ConnectionError:
        log_message("❌ Erreur connexion - Serveur inaccessible")
        return False
    except Exception as e:
        log_message(f"❌ Erreur: {str(e)}")
        return False

def run_keep_alive():
    """Boucle principale du keep-alive."""
    log_message("🚀 RESPIRIA Keep-Alive démarré")
    log_message(f"📡 URL: {API_URL}")
    log_message(f"⏱️ Intervalle: {PING_INTERVAL // 60} minutes")
    log_message("-" * 50)
    
    # Attendre la connexion internet
    wait_for_internet()
    
    # Premier ping immédiat
    ping_server()
    
    consecutive_failures = 0
    max_failures = 5
    
    while True:
        try:
            time.sleep(PING_INTERVAL)
            
            # Vérifier internet avant de ping
            if not check_internet():
                log_message("📡 Connexion perdue, en attente...")
                wait_for_internet()
                log_message("✅ Reconnecté! Reprise des pings...")
            
            success = ping_server()
            
            if success:
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                if consecutive_failures >= max_failures:
                    log_message(f"🔴 {max_failures} échecs consécutifs - Vérifiez le serveur!")
                    consecutive_failures = 0  # Reset pour continuer
                    
        except KeyboardInterrupt:
            log_message("\n🛑 Keep-Alive arrêté par l'utilisateur")
            break
        except Exception as e:
            log_message(f"❌ Erreur inattendue: {str(e)}")
            time.sleep(60)  # Attendre 1 minute avant de réessayer

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║         RESPIRIA AI - Keep-Alive Service                 ║
║                                                          ║
║  Ce script maintient le serveur Render actif en          ║
║  envoyant un ping toutes les 5 minutes.                  ║
║                                                          ║
║  Appuyez Ctrl+C pour arrêter.                            ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    run_keep_alive()
