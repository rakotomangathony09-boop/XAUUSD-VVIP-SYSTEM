import requests, os, time, threading, pytz
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')

state = {
    "price": "CHARGEMENT...", "sentiment": "50", "cot_bias": "NEUTRAL", 
    "ob": "B:0.0 | A:0.0", "news_name": "AUCUNE NEWS", "countdown": "00:00:00", 
    "judas_signal": "SCANNING", "status": "Initialisation...",
    "news_time": None, "prep_sent": False
}

def send_tg(msg):
    token, chat_id = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        try: requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}&parse_mode=Markdown", timeout=5)
        except: pass

def update_engine():
    while True:
        try:
            api_key = os.getenv("TWELVE_DATA_API_KEY")
            fn_key = os.getenv("FINNHUB_API_KEY")

            # 1. PRIX & ORDER BOOK (Un seul appel groupé pour économiser l'API)
            p_res = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={api_key}", timeout=10).json()
            if 'price' in p_res:
                state["price"] = f"{float(p_res['price']):.2f}"
                state["status"] = "Flux Temps Réel Connecté ✅"
            else:
                state["status"] = "Attente du flux Twelve Data..."

            # 2. NEWS & COUNTDOWN
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
                        diff = e_time - now_utc
                        state["countdown"] = str(timedelta(seconds=max(0, int(diff.total_seconds()))))
                        
                        # ALERTE TELEGRAM (Automatique)
                        if 110 < int(diff.total_seconds()) < 150 and not state["prep_sent"]:
                            send_tg(f"⚠️ *PRÉPARATION VVIP*\nNews : {state['news_name']}\nManipulation attendue dans 2 min.")
                            state["prep_sent"] = True
                        break
        except:
            state["status"] = "Erreur de connexion aux serveurs..."
        
        time.sleep(45) # DELAI CRUCIAL pour ne pas être banni par l'API gratuite

class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self): self.send_response(200); self.end_headers()
    def do_GET(self):
        self.send_response(200); self.send_header("Content-type", "text/html; charset=utf-8"); self.end_headers()
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
    threading.Thread(target=update_engine, daemon=True).start()
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), Handler).serve_forever()
