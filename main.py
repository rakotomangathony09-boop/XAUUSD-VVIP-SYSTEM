import requests, os, time, threading, pytz
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')

state = {
    "price": 0.0, "sentiment": 0, "ob": "...", 
    "news_name": "Initialisation...", "news_time": None, "countdown": "00:00:00",
    "active_trade": False, "entry": 0.0, "prep_sent": False
}

def get_next_news():
    """Récupère la news USD à venir via Finnhub."""
    try:
        api_key = os.getenv("FINNHUB_API_KEY")
        curr_date = datetime.now().strftime('%Y-%m-%d')
        url = f"https://finnhub.io/api/v1/calendar/economic?from={curr_date}&to={curr_date}&token={api_key}"
        res = requests.get(url).json()
        
        upcoming = []
        now_utc = datetime.now(pytz.utc)
        
        for event in res.get('economicCalendar', []):
            event_time = datetime.fromisoformat(event['time'].replace('Z', '+00:00'))
            if event['country'] == 'USD' and event['impact'] in ['high', 'medium'] and event_time > now_utc:
                upcoming.append(event)
        
        if upcoming:
            next_e = min(upcoming, key=lambda x: x['time'])
            state["news_name"] = next_e['event']
            state["news_time"] = datetime.fromisoformat(next_e['time'].replace('Z', '+00:00'))
    except: pass

def update_countdown():
    if state["news_time"]:
        diff = state["news_time"] - datetime.now(pytz.utc)
        if diff.total_seconds() > 0:
            state["countdown"] = str(timedelta(seconds=int(diff.total_seconds())))
        else:
            state["countdown"] = "00:00:00"
            state["news_time"] = None # Reset pour chercher la suivante

def send_tg(msg):
    t = os.getenv("TELEGRAM_BOT_TOKEN")
    c = os.getenv("TELEGRAM_CHAT_ID")
    requests.get(f"https://api.telegram.org/bot{t}/sendMessage?chat_id={c}&text={msg}&parse_mode=Markdown")

def autonomous_engine():
    while True:
        get_next_news()
        update_countdown()
        
        # Récupération DATA
        api_key = os.getenv("TWELVE_DATA_API_KEY")
        p_res = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={api_key}").json()
        ob_res = requests.get(f"https://api.twelvedata.com/order_book?symbol=XAU/USD&apikey={api_key}").json()
        
        if 'price' in p_res:
            state["price"] = float(p_res['price'])
            bids = sum([float(b['size']) for b in ob_res.get('bids', [])[:5]])
            asks = sum([float(a['size']) for a in ob_res.get('asks', [])[:5]])
            state["ob"] = f"B:{bids:.1f} | A:{asks:.1f}"

            # LOGIQUE : Alerte Préparation 2 min avant News
            if "0:02:" in state["countdown"] and not state["prep_sent"]:
                send_tg(f"⚠️ *PRÉPARATION NEWS VVIP*\n\nEvénement : {state['news_name']}\nCompte à rebours : 2 minutes.\nSoyez prêt pour le Judas Swing.")
                state["prep_sent"] = True

            # SIGNAL NEWS (Déséquilibre Order Book violent pendant la news)
            if state["countdown"] == "00:00:00" and not state["active_trade"]:
                if bids > (asks * 1.5):
                    send_tg(f"🚀 *NEWS SIGNAL BUY*\nNews : {state['news_name']}\nEntrée : {state['price']}\nTP : +100 Pips\nBE : à +50 Pips")
                    state["active_trade"] = True
                elif asks > (bids * 1.5):
                    send_tg(f"🚀 *NEWS SIGNAL SELL*\nNews : {state['news_name']}\nEntrée : {state['price']}\nTP : +100 Pips\nBE : à +50 Pips")
                    state["active_trade"] = True

        time.sleep(1)

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        with open("index.html", "r") as f: html = f.read()
        for k, v in state.items(): html = html.replace(f"{{{{{k.upper()}}}}}", str(v))
        self.wfile.write(html.encode())

if __name__ == "__main__":
    threading.Thread(target=autonomous_engine, daemon=True).start()
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), Server).serve_forever()
