import requests, os, time, threading, pytz
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')

# État global avec valeurs de secours pour éviter l'affichage des balises {{}}
state = {
    "price": "0.00", "sentiment": "50", "cot_bias": "CALCUL...", "ob": "FLUX REEL...",
    "news_name": "AUCUNE NEWS", "countdown": "00:00:00", "judas_signal": "SCANNING",
    "status": "Connexion aux flux institutionnels...", "news_time": None,
    "active_trade": False, "prep_sent": False
}

def sync_logic():
    """Logique centrale de récupération des données réelles."""
    try:
        api_key = os.getenv("TWELVE_DATA_API_KEY")
        fn_key = os.getenv("FINNHUB_API_KEY")
        user, pw = os.getenv("MYFXBOOK_EMAIL"), os.getenv("MYFXBOOK_PASSWORD")

        # 1. PRIX & ORDER BOOK
        p_res = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={api_key}", timeout=10).json()
        ob_res = requests.get(f"https://api.twelvedata.com/order_book?symbol=XAU/USD&apikey={api_key}", timeout=10).json()
        
        if 'price' in p_res: state["price"] = f"{float(p_res['price']):.2f}"
        if 'bids' in ob_res:
            b_vol = sum([float(b['size']) for b in ob_res['bids'][:5]])
            a_vol = sum([float(a['size']) for a in ob_res['asks'][:5]])
            state["ob"] = f"B:{b_vol:.1f} | A:{a_vol:.1f}"

        # 2. SENTIMENT & COT
        log = requests.get(f"https://api.myfxbook.com/api/login.json?email={user}&password={pw}", timeout=10).json()
        if log.get('session'):
            outlook = requests.get(f"https://api.myfxbook.com/api/get-community-outlook.json?session={log['session']}", timeout=10).json()
            for item in outlook.get('symbols', []):
                if item['name'] == "XAUUSD":
                    s_val = int(item['shortPercentage'])
                    state["sentiment"] = str(s_val)
                    state["cot_bias"] = "INSTITUTIONAL BUY" if s_val >= 60 else "INSTITUTIONAL SELL" if s_val <= 40 else "NEUTRAL"

        # 3. NEWS & COUNTDOWN
        c_date = datetime.now().strftime('%Y-%m-%d')
        n_res = requests.get(f"https://finnhub.io/api/v1/calendar/economic?from={c_date}&to={c_date}&token={fn_key}", timeout=10).json()
        now_utc = datetime.now(pytz.utc)
        upcoming = [e for e in n_res.get('economicCalendar', []) if e['country'] == 'USD' and e['impact'] in ['high', 'medium']]
        
        if upcoming:
            for e in sorted(upcoming, key=lambda x: x['time']):
                e_time = datetime.fromisoformat(e['time'].replace('Z', '+00:00'))
                if e_time > now_utc:
                    state["news_name"] = e['event']
                    state["news_time"] = e_time
                    break
    except Exception as e:
        state["status"] = f"Erreur Flux: {str(e)}"

def autonomous_loop():
    """Boucle de mise à jour permanente."""
    while True:
        sync_logic()
        if state["news_time"]:
            diff = state["news_time"] - datetime.now(pytz.utc)
            state["countdown"] = str(timedelta(seconds=max(0, int(diff.total_seconds()))))
        time.sleep(10) # Rafraîchissement toutes les 10s pour économiser l'API

class VVIPHandler(BaseHTTPRequestHandler):
    def do_HEAD(self): 
        self.send_response(200); self.end_headers()
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        with open("index.html", "r", encoding="utf-8") as f: html = f.read()
        
        mapping = {
            "{{TIME}}": datetime.now(MADAGASCAR_TZ).strftime('%H:%M:%S'),
            "{{PRICE}}": state["price"],
            "{{SENTIMENT}}": state["sentiment"],
            "{{COT_BIAS}}": state["cot_bias"],
            "{{OB}}": state["ob"],
            "{{NEWS_NAME}}": state["news_name"],
            "{{COUNTDOWN}}": state["countdown"],
            "{{JUDAS_SIGNAL}}": state["judas_signal"],
            "{{STATUS}}": state["status"]
        }
        for k, v in mapping.items(): html = html.replace(k, str(v))
        self.wfile.write(html.encode('utf-8'))

if __name__ == "__main__":
    sync_logic() # Synchronisation immédiate avant le démarrage du serveur
    threading.Thread(target=autonomous_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), VVIPHandler).serve_forever()
