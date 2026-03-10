import requests
import os
import time

# --- CONFIGURATION SÉCURISÉE VIA RENDER ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
EMAIL = os.getenv("MYFXBOOK_EMAIL")
PASSWORD = os.getenv("MYFXBOOK_PASSWORD")

def get_session():
    url = f"https://api.myfxbook.com/api/login.json?email={EMAIL}&password={PASSWORD}"
    try:
        # Attente de sécurité pour le réseau Render
        time.sleep(2)
        r = requests.get(url, timeout=15).json()
        return r['session'] if not r.get('error') else None
    except: return None

def get_market_data(session):
    sent_url = f"https://api.myfxbook.com/api/get-community-outlook.json?session={session}"
    price_url = f"https://api.twelvedata.com/quote?symbol=XAU/USD&apikey={API_KEY}"
    try:
        sent_res = requests.get(sent_url, timeout=15).json()
        price_res = requests.get(price_url, timeout=15).json()
        short_pct = next(item['shortPercentage'] for item in sent_res['symbols'] if item['name'] == "XAUUSD")
        return {
            "price": float(price_res['close']),
            "high": float(price_res['high']),
            "low": float(price_res['low']),
            "sentiment_short": float(short_pct)
        }
    except: return None

def execute_sniper():
    print("🔍 Analyse du marché en cours...")
    session = get_session()
    if not session: 
        print("❌ Erreur de session Myfxbook")
        return
    
    data = get_market_data(session)
    if not data: return

    price = data['price']
    short_pct = data['sentiment_short']
    
    # --- LOGIQUE CONTRARIENNE (SEUIL 60%) ---
    if short_pct >= 60:
        side, sl, tp1, tp2 = "BUY", round(data['low'] - 1.2, 2), round(price + 10, 2), round(price + 15, 2)
        send_telegram(side, price, sl, tp1, tp2, short_pct)
    elif short_pct <= 40:
        side, sl, tp1, tp2 = "SELL", round(data['high'] + 1.2, 2), round(price - 10, 2), round(price - 15, 2)
        send_telegram(side, price, sl, tp1, tp2, (100 - short_pct))

def send_telegram(side, price, sl, tp1, tp2, sent):
    msg = (f"🎯 **SNIPER SIGNAL VVIP** 🚀\n"
           f"--------------------------\n"
           f"🔥 SENTIMENT : {sent}%\n"
           f"💧 LIQUIDITY : High/Low Swept\n"
           f"--------------------------\n"
           f"🚀 TYPE: {side} NOW\n"
           f"📍 ENTRY: {price}\n"
           f"--------------------------\n"
           f"✅ TP 1: {tp1}\n"
           f"✅ TP 2: {tp2}\n"
           f"🛡️ SL: {sl}\n"
           f"--------------------------\n"
           f"© Mc Anthonio Sniper")
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    print(f"✅ Signal {side} envoyé !")

if __name__ == "__main__":
    print("🚀 Robot Sniper VVIP Actif - Signature: Mc Anthonio")
    while True:
        try:
            execute_sniper()
        except Exception as e:
            print(f"⚠️ Erreur mineure : {e}")
        
        # Pause de 15 minutes entre chaque scan (900 secondes)
        time.sleep(900)
