import requests, os, time, threading, pytz
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- CONFIGURATION VVIP ---
MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
MYFX_USER = os.getenv("MYFXBOOK_EMAIL")
MYFX_PASS = os.getenv("MYFXBOOK_PASSWORD")

state = {
    "price": "CHARGEMENT...", 
    "sentiment": "50", 
    "cot": "SCANNING",
    "day_summary": "Initialisation... Scan OANDA & Myfxbook en cours.",
    "last_signal": None
}

def send_tele(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def update_and_monitor():
    print("Démarrage du moteur d'analyse...")
    send_tele("✅ **SYSTÈME VVIP CONNECTÉ**\n---\nLe terminal d'Anthonio est en ligne et scanne les marchés.")

    while True:
        try:
            # 1. PRIX
            p_res = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={API_KEY}", timeout=10).json()
            if 'price' in p_res:
                state["price"] = p_res['price']
            
            curr_p = float(state["price"]) if state["price"] != "CHARGEMENT..." else 0

            # 2. SENTIMENT & BIAIS
            log = requests.get(f"https://api.myfxbook.com/api/login.json?email={MYFX_USER}&password={MYFX_PASS}", timeout=10).json()
            if not log.get('error'):
                sess = log['session']
                out = requests.get(f"https://api.myfxbook.com/api/get-community-outlook.json?session={sess}", timeout=10).json()
                for s in out.get('symbols', []):
                    if s['name'] == "XAUUSD":
                        state["sentiment"] = s['shortPercentage']
                        state["cot"] = "BULLISH" if int(state["sentiment"]) > 60 else "BEARISH"

            state["day_summary"] = f"Biais {state['cot']} détecté. Le Judas Model surveille les zones de liquidité sur le graphique OANDA."
        except Exception as e: 
            print(f"Erreur Update: {e}")
        time.sleep(30) # Mise à jour toutes les 30 secondes

class VVIPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        try:
            with open("index.html", "r", encoding="utf-8") as f: 
                content = f.read()
            
            # Remplacement ligne par ligne (Zéro risque de bug)
            content = content.replace("{{PRICE}}", str(state["price"]))
            content = content.replace("{{SENTIMENT}}", str(state["sentiment"]))
            content = content.replace("{{COT_BIAS}}", str(state["cot"]))
            content = content.replace("{{DAY_SUMMARY}}", str(state["day_summary"]))
            content = content.replace("{{TIME}}", datetime.now(MADAGASCAR_TZ).strftime('%H:%M:%S'))
            
            self.wfile.write(content.encode('utf-8'))
        except Exception as e: 
            self.wfile.write(f"Erreur serveur interne : {e}".encode('utf-8'))

if __name__ == "__main__":
    threading.Thread(target=update_and_monitor, daemon=True).start()
    print("Serveur Web démarré sur le port 10000...")
    HTTPServer(('0.0.0.0', 10000), VVIPHandler).serve_forever()
