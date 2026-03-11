import requests, os, time, threading, pytz
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

# Configuration Madagascar (EAT)
MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')

state = {
    "news_name": "SCANNING...", 
    "countdown": "00:00:00", 
    "judas_signal": "EN ATTENTE D'OPPORTUNITÉ", 
    "status": "Moteur Algorithmique Actif ✅",
    "probability": "0%",
    "suggestion": "Analyse du marché en cours...",
    "news_time": None, 
    "prep_sent": False
}

def is_killzone():
    now = datetime.now(MADAGASCAR_TZ)
    return (10 <= now.hour <= 13) or (15 <= now.hour <= 18)

def calculate_real_metrics(impact):
    in_kz = is_killzone()
    if impact == 'high' and in_kz:
        prob, sugg = "90% (Hautement Probable)", "🔥 SIGNAL SNIPER : Ouvrir 3 à 5 positions (0.01/100$)"
    elif impact == 'high' or (impact == 'medium' and in_kz):
        prob, sugg = "75% (Confirmé)", "⚡ SIGNAL CONFIRMÉ : Ouvrir 2 positions (0.01/100$)"
    else:
        prob, sugg = "60% (Modéré)", "🛡️ SIGNAL PRUDENT : 1 seule position (Gestion stricte)"
    return prob, sugg

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
            fn_key = os.getenv("FINNHUB_API_KEY")
            c_date = datetime.now().strftime('%Y-%m-%d')
            n_res = requests.get(f"https://finnhub.io/api/v1/calendar/economic?from={c_date}&to={c_date}&token={fn_key}", timeout=10).json()
            now_utc = datetime.now(pytz.utc)
            upcoming = [e for e in n_res.get('economicCalendar', []) if e['country'] == 'USD' and e['impact'] in ['high', 'medium']]
            if upcoming:
                for e in sorted(upcoming, key=lambda x: x['time']):
                    e_time = datetime.fromisoformat(e['time'].replace('Z', '+00:00'))
                    if e_time > now_utc:
                        state["news_name"], state["news_time"] = e['event'], e_time
                        diff = e_time - now_utc
                        state["countdown"] = str(timedelta(seconds=max(0, int(diff.total_seconds()))))
                        state["probability"], state["suggestion"] = calculate_real_metrics(e['impact'])
                        if 110 < int(diff.total_seconds()) < 130 and not state["prep_sent"]:
                            state["judas_signal"] = "🎯 SIGNAL SNIPER ACTIF"
                            msg = (f"🚀 *NOUVEAU SIGNAL VVIP*\n\n📈 **Instrument :** GOLD (XAU/USD)\n📢 **News :** {state['news_name']}\n💎 **Probabilité :** {state['probability']}\n\n🛡️ **SL :** -30 Pips\n🎯 **TP 1 :** +50 Pips\n🎯 **TP 2 :** +100 Pips\n\n💡 **Suggestion :**\n{state['suggestion']}\n\n⚖️ *Gestion : Déplacez au BE à +30 Pips.*\n👤 *Anthonio Michel RAKOTOMANGA*")
                            send_tg(msg); state["prep_sent"] = True
                        break
            else:
                state["news_name"], state["probability"], state["suggestion"] = "Attente News USD", "Scanning...", "Attente SMC Setup"
        except: state["status"] = "Connexion flux..."
        time.sleep(30)

class VVIPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-type", "text/html; charset=utf-8"); self.end_headers()
        try:
            with open("index.html", "r", encoding="utf-8") as f: html = f.read()
            mapping = {"{{TIME}}": datetime.now(MADAGASCAR_TZ).strftime('%H:%M:%S'), "{{NEWS_NAME}}": state["news_name"], "{{COUNTDOWN}}": state["countdown"], "{{JUDAS_SIGNAL}}": state["judas_signal"], "{{STATUS}}": state["status"], "{{PROBABILITY}}": state["probability"], "{{SUGGESTION}}": state["suggestion"]}
            for k, v in mapping.items(): html = html.replace(k, str(v))
            self.wfile.write(html.encode('utf-8'))
        except: pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=update_engine, daemon=True).start()
    HTTPServer(('0.0.0.0', port), VVIPHandler).serve_forever()
