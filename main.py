import requests, os, time, threading, pytz
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# Configuration
MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
MYFX_USER = os.getenv("MYFXBOOK_EMAIL")
MYFX_PASS = os.getenv("MYFXBOOK_PASSWORD")

# État des données
state = {
    "price": "Connexion...",
    "sentiment": "Analyse",
    "cot": "SCANNING",
    "day_summary": "Synchronisation des serveurs institutionnels..."
}

def update_data():
    """Boucle de mise à jour des données réelles."""
    while True:
        try:
            # 1. PRIX (Twelve Data)
            p_res = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={API_KEY}", timeout=10).json()
            if 'price' in p_res:
                state["price"] = f"{float(p_res['price']):.2f}"
            
            # 2. SENTIMENT (Myfxbook)
            log = requests.get(f"https://api.myfxbook.com/api/login.json?email={MYFX_USER}&password={MYFX_PASS}", timeout=10).json()
            if log.get('session'):
                sess = log['session']
                out = requests.get(f"https://api.myfxbook.com/api/get-community-outlook.json?session={sess}", timeout=10).json()
                for s in out.get('symbols', []):
                    if s['name'] == "XAUUSD":
                        state["sentiment"] = s['shortPercentage']
                        state["cot"] = "BULLISH" if int(state["sentiment"]) > 60 else "BEARISH"
            
            state["day_summary"] = f"Analyse terminée. Biais {state['cot']} détecté sur l'Or."
        except:
            pass
        time.sleep(30)

class VVIPHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        """Répond aux tests de Render pour éviter l'erreur 501."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        """Affiche le terminal avec les vraies données."""
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        try:
            with open("index.html", "r", encoding="utf-8") as f:
                content = f.read()
            
            # Remplacement pour affichage réel
            final_html = content.replace("{{PRICE}}", str(state["price"]))
            final_html = final_html.replace("{{SENTIMENT}}", str(state["sentiment"]))
            final_html = final_html.replace("{{COT_BIAS}}", str(state["cot"]))
            final_html = final_html.replace("{{DAY_SUMMARY}}", str(state["day_summary"]))
            final_html = final_html.replace("{{TIME}}", datetime.now(MADAGASCAR_TZ).strftime('%H:%M:%S'))
            
            self.wfile.write(final_html.encode('utf-8'))
        except:
            self.wfile.write(b"Erreur critique d'affichage.")

if __name__ == "__main__":
    # Lancement du scanner
    threading.Thread(target=update_data, daemon=True).start()
    # Configuration du port Render
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), VVIPHandler)
    print(f"Terminal en ligne sur le port {port}")
    server.serve_forever()
