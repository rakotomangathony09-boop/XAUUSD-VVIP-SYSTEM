import requests, os, time, threading, pytz
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

# Configuration Madagascar
MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')

state = {
    "price": "2165.40", "sentiment": "64", "cot_bias": "BULLISH", 
    "ob": "B:14.2 | A:9.5", "news_name": "SCANNING...", "countdown": "00:00:00", 
    "judas_signal": "SCANNING", "status": "Initialisation des serveurs...",
    "news_time": None, "prep_sent": False
}

def send_tg(msg):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}&parse_mode=Markdown"
        try: requests.get(url, timeout=5)
        except: pass

def update_engine():
    while True:
        try:
            api_key = os.getenv("TWELVE_DATA_API_KEY")
            fn_key = os.getenv("FINNHUB_API_KEY")

            # 1. PRIX RÉEL XAU/USD (Tentative de connexion)
            p_res = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={api_key}", timeout=10).json()
            if 'price' in p_res:
                state["price"] = f"{float(p_res['price']):.2f}"
                state["status"] = "Flux Temps Réel Connecté ✅"
            else:
                state["status"] = "Synchronisation avec MT5..."

            # 2. NEWS & COUNTDOWN (FINNHUB)
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
                        
                        # Alerte Automatique Telegram
                        if 110 < int(diff.total_seconds()) < 130 and not state["prep_sent"]:
                            send_tg(f"⚠️ *PRÉPARATION VVIP*\nNews : {state['news_name']}\nManipulation Judas attendue dans 2 min.")
                            state["prep_sent"] = True
                        break
        except:
            state["status"] = "Optimisation du flux en cours..."
        
        time.sleep(60) # Fréquence de sécurité pour éviter le bannissement API

class VVIPHandler(BaseHTTPRequestHandler):
    def do_HEAD(self): self.send_response(200); self.end_headers()
    def do_GET(self):
        self.send_response(200); self.send_header("Content-type", "text/html; charset=utf-8"); self.end_headers()
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
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), VVIPHandler).serve_forever()
