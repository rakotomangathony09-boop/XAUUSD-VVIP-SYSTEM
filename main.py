import requests, os, time, threading, pytz
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- CONFIGURATION (Assure-toi que ces variables sont sur Render) ---
MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVE_DATA_API_KEY")

def send_tele(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, data=payload, timeout=10)
        print(f"Telegram Status: {r.status_code}")
    except Exception as e:
        print(f"Erreur Telegram: {e}")

def run_immediate_test():
    """Envoie une séquence de signal complète pour valider le système"""
    print("🛠️ DÉMARRAGE DU TEST DE FORCE...")
    
    # 1. Vérification API Prix
    try:
        p_res = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={API_KEY}", timeout=10).json()
        price = p_res.get('price', "2150.00")
    except:
        price = "2150.00 (Mode Démo)"

    # 2. SIGNAL SNIPER IMMEDIAT
    msg_signal = (
        f"🎯 **[TEST FORCE] SIGNAL SNIPER VVIP**\n---\n"
        f"🚀 TYPE : **BUY NOW**\n"
        f"📍 ENTRY : {price}\n"
        f"💰 TP 1 : {float(price.split('.')[0])+10} (+100 Pips)\n"
        f"🏆 TP FINAL : {float(price.split('.')[0])+25}\n"
        f"🛡️ SL : {float(price.split('.')[0])-8}\n---\n"
        f"📊 SUGGESTION : 🚀 3 POSITIONS\n"
        f"💡 ACTION : BE à +50 pips.\n---\n"
        f"© Anthonio Michel RAKOTOMANGA"
    )
    send_tele(msg_signal)
    
    # 3. MISE À JOUR BREAKEVEN (après 15 secondes)
    time.sleep(15)
    send_tele(f"🛡️ **[TEST FORCE] MISE À JOUR : BE**\n---\nLe prix a atteint +50 pips. Sécurisation à l'entrée effectuée ✅")
    
    # 4. MISE À JOUR TP1 (après 15 secondes)
    time.sleep(15)
    send_tele(f"✅ **[TEST FORCE] TP 1 TOUCHÉ (+100 PIPS)**\n---\n50% des profits encaissés. On laisse courir le reste !")

class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>SYSTEME VVIP EN LIGNE - TEST DE FORCE LANCE</h1>")

if __name__ == "__main__":
    # Lancement du serveur Web (pour éviter l'erreur 502)
    server_thread = threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), SimpleServer).serve_forever(), daemon=True)
    server_thread.start()
    
    # Exécution du test
    run_immediate_test()
    
    # Garder le script en vie
    while True:
        time.sleep(10)
