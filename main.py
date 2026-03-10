import requests
import time
import os

# --- CONFIGURATION (Récupérée depuis les variables Render) ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
SYMBOL = "XAU/USD"

def get_market_analysis():
    """Récupère le prix et calcule la volatilité pour un SL intelligent"""
    url = f"https://api.twelvedata.com/quote?symbol={SYMBOL}&apikey={API_KEY}"
    try:
        response = requests.get(url).json()
        if 'close' in response:
            price = float(response['close'])
            high = float(response['high'])
            low = float(response['low'])
            # Calcul de la zone de liquidité (20% de la volatilité journalière)
            smart_buffer = (high - low) * 0.15 
            return price, smart_buffer
    except Exception as e:
        print(f"Erreur API: {e}")
    return None, None

def send_sniper_signal(price, buffer, side):
    """Calcule les Multi-TP et envoie le signal automatique"""
    
    if side == "BUY":
        # SL placé intelligemment sous la liquidité récente
        sl = round(price - (buffer + 1.5), 2)
        tp1 = round(price + 10.0, 2)  # +100 Pips
        tp2 = round(price + 15.0, 2)  # +150 Pips
    else:
        # SL placé intelligemment au-dessus de la liquidité
        sl = round(price + (buffer + 1.5), 2)
        tp1 = round(price - 10.0, 2)
        tp2 = round(price - 15.0, 2)

    message = (
        f"🚀 **XAUUSD SNIPER SYSTEM** 🚀\n"
        f"--------------------------\n"
        f"🔥 TYPE: {side} NOW\n"
        f"📍 ENTRY: {price}\n"
        f"--------------------------\n"
        f"✅ TP 1: {tp1} (+100 Pips)\n"
        f"✅ TP 2: {tp2} (+150 Pips)\n"
        f"🎯 TP FINAL: LIQUIDITY TARGET\n"
        f"--------------------------\n"
        f"🛡️ SMART SL: {sl}\n"
        f"*(Placé selon zone de liquidité)*\n"
        f"--------------------------\n"
        f"© Mc Anthonio Sniper VVIP"
    )
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

# --- SCANNER DE MARCHÉ ---
print("Robot Sniper Multi-TP en ligne...")

while True:
    current_price, smart_buffer = get_market_analysis()
    
    if current_price:
        print(f"Analyse: {current_price} | SL Buffer: {smart_buffer}")
        
        # Le signal s'enverra ici selon tes conditions de sentiment
        # Exemple: if sentiment >= 70: send_sniper_signal(current_price, smart_buffer, "BUY")
        
    # Scan toutes les 15 minutes pour respecter ton quota Twelve Data
    time.sleep(900)
