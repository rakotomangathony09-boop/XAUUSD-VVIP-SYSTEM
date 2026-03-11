import requests, os, time, threading, pytz
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

# Configuration Madagascar
MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')

# État initial (Dynamique)
state = {
    "price": "CHARGEMENT...", "sentiment": "50", "cot_bias": "NEUTRAL", 
    "ob": "B:0.0 | A:0.0", "news_name": "AUCUNE NEWS", "countdown": "00:00:00", 
    "judas_signal": "SCANNING", "status": "Initialisation des flux...",
    "news_time": None, "active_trade": False, "prep_sent": False
}

def send_tg(msg):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}&parse_mode=Markdown"
        try: requests.get(url, timeout=5)
        except: pass

def update_engine():
    """Moteur de données ultra-robuste."""
    while True:
        try:
            api_key = os.getenv("TWELVE_DATA_API_KEY")
            fn_key = os.getenv("FINNHUB_API_KEY")

            # 1. PRIX RÉEL XAU/USD
            p_res = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={api_key}", timeout=10).json()
            if 'price' in p_res:
                state["price"] = f"{float(p_res['price']):.2f}"
                state["status"] = "Flux Temps Réel Connecté ✅"
            elif 'message' in p_res:
                state["status"] = "Limite API atteinte (Attente...)"

            # 2. CALENDRIER NEWS (FINNHUB)
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

            # 3. CALCUL DU COMPTE À REBOURS
            if state["news_time"]:
                diff = state["news_time"] - now_utc
                seconds_left = int(diff.total_seconds())
                state["countdown"] = str(timedelta(seconds=max(0, seconds_left)))

                # Alerte Telegram 2 min avant
                if 115 < seconds_left < 125 and not state["prep_sent"]:
                    send_tg(f"⚠️ *PRÉPARATION VVIP*\nNews : {state['news_name']}\nSignal imminent dans 2 minutes.")
                    state["prep_sent"] = True

        except Exception as e:
            state["status"] = "Ajustement des flux..."
        
        time.sleep(15) # Fréquence optimale pour plan gratuit XII Data

class VVIPServer(BaseHTTPRequestHandler):
    def do_HEAD(self): self.send_response(200); self.end_headers()
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        try:
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
        except: pass

if __name__ == "__main__":
    threading.Thread(target=update_engine, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), VVIPServer).serve_forever()
