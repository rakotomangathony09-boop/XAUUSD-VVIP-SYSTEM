import requests
import time
import os

# --- CONFIGURATION DES CLÉS (À mettre sur Render) ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
SYMBOL = "XAU/USD"

def get_market_data():
    """Récupère le prix actuel et la volatilité pour un SL intelligent"""
    url = f"https://api.twelvedata.com/quote?symbol={SYMBOL}&apikey={API_KEY}"
    response = requests.get(url).json()
    if 'close' in response:
        price = float(response['close'])
        # Simulation d'analyse de liquidité basée sur le range du jour
        high = float(response['high'])
        low = float(response['low'])
        volatility = (high - low) * 0.2  # On place le SL à 20% du range journalier
        return price, volatility
    return None, None

def send_sniper_signal(price, volatility, side):
    """Calcule les TP et le SL Intelligent"""
    
    # 🎯 Calcul du SL Intelligent (Derrière la liquidité)
    # On ajoute une petite marge de sécurité pour éviter les "Stop Hunts"
    if side == "BUY":
        sl = round(price - (volatility + 2.0), 2)
        tp1 = round(price + 10.0, 2) # +100 Pips
        tp2 = round(price + 15.0, 2) # +150 Pips
    else:
        sl = round(price + (volatility + 2.0), 2)
        tp1 = round(price - 10.0, 2)
        tp2 = round(price - 15.0, 2)

    message = (
        f"🎯 **SNIPER ENTRY DETECTED** 🚀\n"
        f"-------------------------\n"
        f"🔥 SYMBOLE: {SYMBOL}\n"
        f"🔥 TYPE: {side} NOW\n"
        f"📍 ENTRY: {price}\n"
        f"-------------------------\n"
        f"✅ TP 1: {tp1} (+100 Pips)\n"
        f"✅ TP 2: {tp2} (+150 Pips)\n"
        f"🎯 TP FINAL: LIQUIDITY TARGET\n"
        f"-------------------------\n"
        f"🛡️ SMART SL: {sl}\n"
        f"*(Placé selon liquidité institutionnelle)*\n"
        f"-------------------------\n"
        f"© Mc Anthonio Sniper VVIP"
    )
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=Markdown"
    requests.get(url)

# --- SCANNER AUTOMATIQUE ---
print("Système Sniper VVIP en cours d'analyse...")

while True:
    price, vol = get_market_data()
    
    if price:
        # Simulation de la condition Sniper (Ex: Sentiment > 70%)
        # if sentiment > 70: 
        #    send_sniper_signal(price, vol, "BUY")
        print(f"Analyse: {price} | Volatilité: {vol}")
        
    # On scanne toutes les 15 min pour rester synchronisé avec Twelve Data
    time.sleep(900)
