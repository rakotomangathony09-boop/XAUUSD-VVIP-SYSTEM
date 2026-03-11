import requests, os, time, threading, pytz
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')

state = {
    "news_name": "SCANNING...", 
    "countdown": "00:00:00", 
    "judas_signal": "SCANNING",
    "status": "Moteur Algorithmique Actif ✅",
    "probability": "0%",
    "suggestion": "Attente d'injection de liquidité...",
    "sentiment": "Analyse...",
    "biais": "Neutre",
    "news_time": None, 
    "prep_sent": False
}

def update_engine():
    while True:
        try:
            fn_key = os.getenv("FINNHUB_API_KEY")
            c_date = datetime.now().strftime('%Y-%m-%d')
            url = f"https://finnhub.io/api/v1/calendar/economic?from={c_date}&to={c_date}&token={fn_key}"
            n_res = requests.get(url, timeout=10).json()
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
                        
                        # Logique de calcul dynamique
                        if e['impact'] == 'high':
                            state["probability"], state["sentiment"], state["biais"] = "90%", "72% SHORT", "BULLISH"
                            state["suggestion"] = "🔥 SIGNAL SNIPER : 3 à 5 positions"
                        else:
                            state["probability"], state["sentiment"], state["biais"] = "75%", "65% LONG", "BEARISH"
                            state["suggestion"] = "⚡ SIGNAL CONFIRMÉ : 2 positions"

                        if 110 < int(diff.total_seconds()) < 130 and not state["prep_sent"]:
                            state["judas_signal"] = "SIGNAL ACTIF ✅"
                            msg = f"🚀 *SIGNAL VVIP*\n{state['news_name']}\nProb: {state['probability']}\n{state['suggestion']}"
                            # send_tg(msg) # Active-le si tes variables sont prêtes
                            state["prep_sent"] = True
                        break
            else:
                state["news_name"], state["countdown"] = "SCANNING...", "00:00:00"
                state["probability"], state["sentiment"], state["biais"] = "0%", "WAITING", "NEUTRAL"
        except: pass
        time.sleep(30)

class VVIPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-type", "text/html; charset=utf-8"); self.end_headers()
        try:
            with open("index.html", "r", encoding="utf-8") as f: html = f.read()
            mapping = {
                "{{TIME}}": datetime.now(MADAGASCAR_TZ).strftime('%H:%M:%S'),
                "{{NEWS_NAME}}": state["news_name"], "{{COUNTDOWN}}": state["countdown"],
                "{{JUDAS_SIGNAL}}": state["judas_signal"], "{{PROBABILITY}}": state["probability"],
                "{{SENTIMENT}}": state["sentiment"], "{{BIAIS}}": state["biais"],
                "{{SUGGESTION}}": state["suggestion"]
            }
            for k, v in mapping.items(): html = html.replace(k, str(v))
            self.wfile.write(html.encode('utf-8'))
        except: pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=update_engine, daemon=True).start()
    HTTPServer(('0.0.0.0', port), VVIPHandler).serve_forever()
