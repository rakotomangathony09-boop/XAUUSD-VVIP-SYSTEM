import requests
import os
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- CONFIGURATION SÉCURISÉE ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
EMAIL = os.getenv("MYFXBOOK_EMAIL")
PASSWORD = os.getenv("MYFXBOOK_PASSWORD")

# --- SERVEUR ANTI-ERREUR RENDER (PORT 10000) ---
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Sniper Bot Active")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- FONCTIONS TECHNIQUES ---
def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

def get_gold_price():
    try:
        url = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={API_KEY}"
        return float(requests.get(url, timeout=10).json()['price'])
    except: return None

# --- SYSTÈME DE SUIVI (TRACKER) ---
def monitor_trade(side, entry, tp, sl):
    print(f"📡 Suivi du trade {side} activé...")
    while True:
        current_price = get_gold_price()
        if not current_price: continue

        if side == "BUY":
            if current_price >= tp:
                send_msg(f"✅ **TP TOUCHÉ !** 💰\n---\n🎯 Signal : BUY\n📍 Prix : {current_price}\n✨ Profit sécurisé !\n---\n© Mc Anthonio")
                break
            if current_price <= sl:
                send_msg(f"❌ **SL TOUCHÉ**\n---\nLe marché a retourné. On attend le prochain setup.\n© Mc Anthonio")
                break
        elif side == "SELL":
            if current_price <= tp:
                send_msg(f"✅ **TP TOUCHÉ !** 💰\n---\n🎯 Signal : SELL\n📍 Prix : {current_price}\n✨ Profit sécurisé !\n---\n© Mc Anthonio")
                break
            if current_price >= sl:
                send_msg(f"❌ **SL TOUCHÉ**\n---\n© Mc Anthonio")
                break
        time.sleep(60) # Vérification chaque minute

# --- LOGIQUE DE SIGNAL ---
def execute_sniper():
    # Force Signal au démarrage pour test
    send_msg("🚀 **FORCE SIGNAL TEST**\n---\nTerminal Render : Connecté ✅\nGroupe Telegram : Lié ✅\nStratégie : Sniper VVIP\n---\n© Mc Anthonio Sniper")
    
    price = get_gold_price()
    if not price: return

    # Ici la stratégie (Exemple 60% sentiment)
    # Pour le test, on simule un signal immédiat
    side = "BUY"
    tp = round(price + 2.0, 2)
    sl = round(price - 1.5, 2)
    
    msg = (f"🎯 **SNIPER SIGNAL VVIP** 🚀\n"
           f"--------------------------\n"
           f"🚀 TYPE: {side} NOW\n"
           f"📍 ENTRY: {price}\n"
           f"✅ TP: {tp}\n"
           f"🛡️ SL: {sl}\n"
           f"--------------------------\n"
           f"© Mc Anthonio Sniper")
    
    send_msg(msg)
    # Lance le suivi sans bloquer le reste du programme
    threading.Thread(target=monitor_trade, args=(side, price, tp, sl), daemon=True).start()

if __name__ == "__main__":
    print("Robot lancé...")
    execute_sniper()
    while True:
        time.sleep(3600)
