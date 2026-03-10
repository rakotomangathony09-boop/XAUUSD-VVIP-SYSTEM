import requests, os, time, threading, pytz
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
MYFX_USER = os.getenv("MYFXBOOK_EMAIL")
MYFX_PASS = os.getenv("MYFXBOOK_PASSWORD")

state = {"price": "0.00", "sentiment": "50", "cot": "BULLISH"}

def update_data():
    try:
        # Prix
        p = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={API_KEY}").json()
        state["price"] = p.get('price', state["price"])
        # Sentiment & COT (Via Myfxbook)
        log = requests.get(f"https://api.myfxbook.com/api/login.json?email={MYFX_USER}&password={MYFX_PASS}").json()
        if not log.get('error'):
            out = requests.get(f"https://api.myfxbook.com/api/get-community-outlook.json?session={log['session']}").json()
            for s in out.get('symbols', []):
                if s['name'] == "XAUUSD":
                    state["sentiment"] = s['shortPercentage']
                    state["cot"] = "INSTITUTIONAL BUY" if int(state["sentiment"]) > 60 else "INSTITUTIONAL SELL"
    except: pass

class BloombergServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        # Lecture du fichier HTML séparé
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remplacement des données dynamiques
        content = content.replace("{{PRICE}}", state["price"])
        content = content.replace("{{SENTIMENT}}", state["sentiment"])
        content = content.replace("{{COT_BIAS}}", state["cot"])
        content = content.replace("{{TIME}}", datetime.now(MADAGASCAR_TZ).strftime('%H:%M:%S'))
        
        self.send_header("Content-Length", len(content))
        self.wfile.write(content.encode())

def sniper_engine():
    while True:
        update_data()
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), BloombergServer).serve_forever(), daemon=True).start()
    sniper_engine()
