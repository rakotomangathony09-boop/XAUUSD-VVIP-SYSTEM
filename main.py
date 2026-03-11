import requests, os, time, threading, pytz
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
MYFX_USER = os.getenv("MYFXBOOK_EMAIL")
MYFX_PASS = os.getenv("MYFXBOOK_PASSWORD")

state = {
    "price": "---", "sentiment": "50", "cot": "SCANNING",
    "day_summary": "Initialisation du Judas Model. Surveillance du flux OANDA...",
    "last_signal": None
}

def update_all():
    try:
        # PRIX XII DATA
        p_res = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={API_KEY}", timeout=10).json()
        state["price"] = p_res.get('price', "---")
        
        # SENTIMENT MYFXBOOK
        log = requests.get(f"https://api.myfxbook.com/api/login.json?email={MYFX_USER}&password={MYFX_PASS}", timeout=10).json()
        if not log.get('error'):
            out = requests.get(f"https://api.myfxbook.com/api/get-community-outlook.json?session={log['session']}", timeout=10).json()
            for s in out.get('symbols', []):
                if s['name'] == "XAUUSD":
                    state["sentiment"] = s['shortPercentage']
                    state["cot"] = "BULLISH" if int(state["sentiment"]) > 60 else "BEARISH"
        
        state["day_summary"] = f"Biais institutionnel {state['cot']}. Le Judas Model attend une manipulation de liquidité sur XAU/USD."
    except: pass

class VVIPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-type", "text/html"); self.end_headers()
        try:
            with open("index.html", "r", encoding="utf-8") as f: content = f.read()
            # Remplacement des variables
            final = content.replace("{{PRICE}}", str(state["price"])) \
                           .replace("{{SENTIMENT}}", str(state["sentiment"])) \
                           .replace("{{COT_BIAS}}", str(state["cot"])) \
                           .replace("{{DAY_SUMMARY}}", str(state["day_summary"])) \
                           .replace("{{TIME}}", datetime.now(MADAGASCAR_TZ).strftime('%H:%M:%S'))
            self.wfile.write(final.encode('utf-8'))
        except: self.wfile.write(b"Erreur de chargement du template.")

if __name__ == "__main__":
    threading.Thread(target=lambda: (update_all(), time.sleep(45)), daemon=True).start()
    HTTPServer(('0.0.0.0', 10000), VVIPHandler).serve_forever()
