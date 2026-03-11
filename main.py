import requests, os, time, threading, pytz
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# Fuseau horaire Madagascar
MADAGASCAR_TZ = pytz.timezone('Indian/Antananarivo')

# État des données (Valeurs par défaut avant connexion)
state = {
    "price": "Connexion...",
    "sentiment": "Analyse",
    "cot": "SCANNING",
    "day_summary": "Initialisation du flux institutionnel..."
}

def update_data_background():
    """Récupère les données réelles en arrière-plan."""
    while True:
        try:
            # 1. PRIX RÉEL (Twelve Data)
            api_key = os.getenv("TWELVE_DATA_API_KEY")
            p_res = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={api_key}", timeout=10).json()
            if 'price' in p_res:
                state["price"] = f"{float(p_res['price']):.2f}"

            # 2. SENTIMENT RÉEL (Myfxbook)
            user = os.getenv("MYFXBOOK_EMAIL")
            pw = os.getenv("MYFXBOOK_PASSWORD")
            log = requests.get(f"https://api.myfxbook.com/api/login.json?email={user}&password={pw}", timeout=10).json()
            
            if log.get('session'):
                sess = log['session']
                out = requests.get(f"https://api.myfxbook.com/api/get-community-outlook.json?session={sess}", timeout=10).json()
                for s in out.get('symbols', []):
                    if s['name'] == "XAUUSD":
                        state["sentiment"] = s['shortPercentage']
                        state["cot"] = "BULLISH" if int(state["sentiment"]) > 60 else "BEARISH"
            
            state["day_summary"] = f"Analyse Sniper terminée. Biais {state['cot']} détecté."
        except:
            pass
        time.sleep(30)

class VVIPServer(BaseHTTPRequestHandler):
    """Gère l'affichage et l'injection des données."""
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        try:
            with open("index.html", "r", encoding="utf-8") as f:
                html = f.read()
            
            # Injection des données réelles
            html = html.replace("{{PRICE}}", str(state["price"]))
            html = html.replace("{{SENTIMENT}}", str(state["sentiment"]))
            html = html.replace("{{COT_BIAS}}", str(state["cot"]))
            html = html.replace("{{DAY_SUMMARY}}", str(state["day_summary"]))
            html = html.replace("{{TIME}}", datetime.now(MADAGASCAR_TZ).strftime('%H:%M:%S'))
            
            self.wfile.write(html.encode('utf-8'))
        except Exception as e:
            self.wfile.write(f"Erreur Serveur: {e}".encode('utf-8'))

if __name__ == "__main__":
    # Lancement du thread de mise à jour
    threading.Thread(target=update_data_background, daemon=True).start()
    
    # Récupération du port Render (Crucial pour éviter 501/502)
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), VVIPServer)
    print(f"Serveur VVIP en ligne sur le port {port}")
    server.serve_forever()
