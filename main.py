import requests, os, time, threading, pytz
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- CONFIGURATION ---
MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVE_DATA_API_KEY")

def send_tele(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def run_force_test():
    print("🚀 LANCEMENT DU TEST DE FORCE...")
    
    # 1. Test de connexion Prix
    p_res = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={API_KEY}").json()
    price = p_res.get('price', "2150.00")
    
    # 2. Envoi du Signal Sniper de Test
    test_msg = (
        f"🎯 **[TEST] SIGNAL SNIPER VVIP**\n---\n"
        f"🚀 TYPE : **BUY NOW**\n"
        f"📍 ENTRY : {price}\n"
        f"💰 TP 1 : {float(price)+10} (+100 Pips)\n"
        f"🏆 TP FINAL : {float(price)+25}\n"
        f"🛡️ SL : {float(price)-8}\n---\n"
        f"📊 SUGGESTION : 🚀 3 POSITIONS\n"
        f"💡 ACTION : BE à +50 pips.\n---\n"
        f"© Mc Anthonio (FORCE TEST)"
    )
    send_tele(test_msg)
    
    # 3. Simulation des mises à jour (toutes les 10 secondes pour le test)
    time.sleep(10)
    send_tele(f"🛡️ **[TEST] MISE À JOUR : BREAKEVEN (BE)**\n---\nLe prix a atteint +50 pips. SL déplacé à l'entrée.")
    
    time.sleep(10)
    send_tele(f"✅ **[TEST] TP 1 TOUCHÉ (+100 PIPS)**\n---\nSécurisation de 50% des profits effectuée.")
    
    print("✅ TEST DE FORCE TERMINÉ AVEC SUCCÈS")

class TestServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b"TEST EN COURS - VERIFIEZ TELEGRAM")

if __name__ == "__main__":
    # Démarre le serveur pour Render
    threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), TestServer).serve_forever(), daemon=True).start()
    # Lance le test immédiatement
    run_force_test()
