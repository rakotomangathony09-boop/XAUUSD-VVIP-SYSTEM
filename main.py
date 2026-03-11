import requests, os, time, threading, pytz
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')

state = {
    "price": "En attente...", 
    "sentiment": "Analyse...", 
    "cot": "SCANNING",
    "day_summary": "Connexion aux flux institutionnels OANDA..."
}

def update_logic():
    while True:
        try:
            # Récupération Prix (TwelveData)
            api_key = os.getenv("TWELVE_DATA_API_KEY")
            p_res = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={api_key}").json()
            if 'price' in p_res:
                state["price"] = f"{float(p_res['price']):.2f}"
            
            # Récupération Sentiment (Myfxbook)
            user = os.getenv("MYFXBOOK_EMAIL")
            pw = os.getenv("MYFXBOOK_PASSWORD")
            log = requests.get(f"https://api.myfxbook.com/api/login.json?email={user}&password={pw}").json()
            if log.get('session'):
                out = requests.get(f"https://api.myfxbook.com/api/get-community-outlook.json?session={log['session']}").json()
                for s in out.get('symbols', []):
                    if s['name'] == "XAUUSD":
                        state["sentiment"] = s['shortPercentage']
                        state["cot"] = "BULLISH" if int(state["sentiment"]) > 60 else "BEARISH"
            
            state["day_summary"] = f"Marché surveillé. Biais actuel : {state['cot']}."
        except:
            pass
        time.sleep(30)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()
        
        # Remplacement manuel ultra-précis
        html = html.replace("{{PRICE}}", state["price"])
        html = html.replace("{{SENTIMENT}}", str(state["sentiment"]))
        html = html.replace("{{COT_BIAS}}", state["cot"])
        html = html.replace("{{DAY_SUMMARY}}", state["day_summary"])
        html = html.replace("{{TIME}}", datetime.now(MADAGASCAR_TZ).strftime('%H:%M:%S'))
        
        self.wfile.write(html.encode('utf-8'))

if __name__ == "__main__":
    threading.Thread(target=update_logic, daemon=True).start()
    HTTPServer(('0.0.0.0', 10000), Handler).serve_forever()
