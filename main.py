import requests
import time
import os

# --- CONFIGURATION ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
SYMBOL = "XAU/USD"

def get_live_price():
    url = f"https://api.twelvedata.com/price?symbol={SYMBOL}&apikey={API_KEY}"
    response = requests.get(url).json()
    return float(response['price']) if 'price' in response else None

def send_telegram_signal(price, side):
    # CALCUL DES MULTIPLES TP
    if side == "BUY":
        tp1 = round(price + 10.0, 2)  # +100 pips
        tp2 = round(price + 15.0, 2)  # +150 pips
        tp_final = "LIQUIDITY TARGET (SMC)"
        sl = round(price - 6.0, 2)    # -60 pips
    else:
        tp1 = round(price - 10.0, 2)
        tp2 = round(price - 15.0, 2)
        tp_final = "LIQUIDITY TARGET (SMC)"
        sl = round(price + 6.0, 2)

    message = (
        f"🚀 **XAUUSD SNIPER SYSTEM**\n"
        f"-------------------------\n"
        f"🔥 TYPE: {side} NOW\n"
        f"📍 ENTRY: {price}\n"
        f"-------------------------\n"
        f"✅ TP 1: {tp1} (+100 Pips)\n"
        f"✅ TP 2: {tp2} (+150 Pips)\n"
        f"🎯 TP FINAL: {tp_final}\n"
        f"🚫 SL: {sl}\n"
        f"-------------------------\n"
        f"© Mc Anthonio Sniper VVIP"
    )
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=Markdown"
    requests.get(url)

# --- BOUCLE DE TRADING (SCANNER) ---
print("Robot Sniper Multi-TP Activé...")
while True:
    price = get_live_price()
    if price:
        # Ici on simule la détection de sentiment 70% pour l'exemple
        # Dans ton vrai bot, c'est ici qu'on met la condition de sentiment
        print(f"Analyse en cours... Prix actuel: {price}")
        
        # Exemple : Si une condition est remplie
        # send_telegram_signal(price, "BUY") 
        
    time.sleep(900) # Scan toutes les 15 minutes pour économiser Twelve Data
