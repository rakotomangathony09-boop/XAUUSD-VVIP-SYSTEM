import requests, os, time, threading, pytz, json
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')

state = {
    "price": "2150.00", "sentiment": "50", "cot_bias": "NEUTRAL", "ob": "B:0.0 | A:0.0",
    "news_name": "AUCUNE NEWS", "countdown": "00:00:00", "judas_signal": "SCANNING",
    "status": "Connexion aux flux...", "news_time": None
}

def clean_fetch():
    """Récupération sécurisée pour éviter l'erreur 'Extra Data'."""
    try:
        api_key = os.getenv("TWELVE_DATA_API_KEY")
        # 1. PRIX (XII DATA)
        p_url = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={api_key}"
        p_res = requests.get(p_url, timeout=10).json()
        if 'price' in p_res:
            state["price"] = f"{float(p_res['price']):.2f}"

        # 2. ORDER BOOK (XII DATA)
        ob_url = f"https://api.twelvedata.com/order_book?symbol=XAU/USD&apikey={api_key}"
        ob_res = requests.get(ob_url, timeout=10).json()
        if 'bids' in ob_res:
            b = sum([float(x['size']) for x in ob_res['bids'][:5]])
            a = sum([float(x['size']) for x in ob_res['asks'][:5]])
            state["ob"] = f"B:{b:.1f} | A:{a:.1f}"

        # 3. NEWS (FINNHUB)
        fn_key = os.getenv("FINNHUB_API_KEY")
        c_date = datetime.now().strftime('%Y-%m-%d')
        n_url = f"https://finnhub.io/api/v1/calendar/economic?from={c_date}&to={c_date}&token={fn_key}"
        n_res = requests.get(n_url, timeout=10).json()
        
        now_utc = datetime.now(pytz.utc)
        events = n_res.get('economicCalendar', [])
        upcoming = [e for e in events if e['country'] == 'USD' and e['impact'] in ['high', 'medium']]
        
        if upcoming:
            for e in sorted(upcoming, key=lambda x: x['time']):
                e_time = datetime.fromisoformat(e['time'].replace('Z', '+00:00'))
                if e_time > now_utc:
                    state["news_name"] = e['event']
                    state["news_time"] = e_time
                    break

        state["status"] = "Flux Temps Réel Connecté ✅"
    except Exception as e:
        state["status"] = f"Ajustement flux en cours..."

def loop():
    while True:
        clean_fetch()
        if state["news_time"]:
            diff = state["news_time"] - datetime.now(pytz.utc)
            state["countdown"] = str(timedelta(seconds=max(0, int(diff.total_seconds()))))
        time.sleep(15)

class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self): self.send_response(200); self.end_headers()
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        with open("index.html", "r", encoding="utf-8") as f: html = f.read()
        
        mapping = {
            "{{TIME}}": datetime.now(MADAGASCAR_TZ).strftime('%H:%M:%S'),
            "{{PRICE}}": state["price"], "{{SENTIMENT}}": state["sentiment"],
            "{{COT_BIAS}}": state["cot_bias"], "{{OB}}": state["ob"],
            "{{NEWS_NAME}}": state["news_name"], "{{COUNTDOWN}}": state["countdown"],
            "{{JUDAS_SIGNAL}}": state["judas_signal"], "{{STATUS}}": state["status"]
        }
        for k, v in mapping.items(): html = html.replace(k, str(v))
        self.wfile.write(html.encode('utf-8'))

if __name__ == "__main__":
    threading.Thread(target=loop, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()
