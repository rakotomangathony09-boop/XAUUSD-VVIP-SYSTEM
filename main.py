import requests
import os
import time

# --- CONFIGURATION SÉCURISÉE ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
EMAIL = os.getenv("MYFXBOOK_EMAIL")
PASSWORD = os.getenv("MYFXBOOK_PASSWORD")

def run_sniper():
    print(f"--- SYSTÈME LANCÉ PAR ANTHONIO MICHEL ---")
    # Petite attente pour stabiliser le réseau au démarrage
    time.sleep(5) 
    
    # Ton code de récupération Myfxbook ici...
    # (Le reste du code reste le même)

if __name__ == "__main__":
    run_sniper()
    # Cette ligne est MAGIQUE : elle garde ton bot allumé 24h/24
    while True:
        time.sleep(3600)
