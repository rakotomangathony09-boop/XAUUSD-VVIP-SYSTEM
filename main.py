import os
import time
import threading
import requests
import telebot
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
from flask import Flask

# --- CONFIGURATION SERVEUR POUR LE PLAN GRATUIT RENDER ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "🔥 Mc Anthonio Sniper Engine est en ligne et analyse le Gold !", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURATION SNIPER ---
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_KEY = os.getenv('TWELVE_DATA_TOKEN')

bot = telebot.TeleBot(TOKEN)
mada_tz = pytz.timezone('Indian/Antananarivo')

def get_live_sentiment():
    """Scraping réel du sentiment MyFXBook"""
    try:
        url = "https://www.myfxbook.com/community/outlook"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr', {'class': 'outlook-symbol-row'})
        for row in rows:
            if 'XAUUSD' in row.text:
                short_perc = row.find('td', {'class': 'short-perc'}).text.replace('%', '')
                return int(short_perc)
        return 0
    except Exception as e:
        print(f"Erreur Sentiment: {e}")
        return 0

def get_live_price():
    """Prix réel XAU/USD via Twelve Data"""
    try:
        url = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={API_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        return float(data['price'])
    except Exception as e:
        print(f"Erreur Prix: {e}")
        return None

def is_market_open():
    now = datetime.now(mada_tz)
    # Fermé le Samedi et Dimanche matin (heure Mada)
    if now.weekday() == 5 or (now.weekday() == 6 and now.hour < 23):
        return False
    return True

def send_sniper_signal(price, sentiment):
    """Envoi du signal réel basé sur l'analyse"""
    tp = round(price + 15.0, 2)
    sl = round(price - 6.0, 2)
    msg = (
        f"🚀 **XAUUSD SNIPER VVIP** 🚀\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📍 TYPE: **BUY NOW**\n"
        f"💰 ENTRY: {price}\n"
        f"✅ TP: {tp}\n"
        f"🛑 SL: {sl}\n"
        f"📊 ANALYSE: Sentiment {sentiment}% Short\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⌚ Heure Mada: {datetime.now(mada_tz).strftime('%H:%M')}\n"
        f"© VVIP Signal by Mc Anthonio"
    )
    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')

def trading_loop():
    print("🔥 ANALYSE RÉELLE ACTIVÉE - ATTENTE DU SEUIL 70%")
    while True:
        if is_market_open():
            sentiment = get_live_sentiment()
            price = get_live_price()
            
            print(f"[{datetime.now(mada_tz).strftime('%H:%M')}] Sentiment: {sentiment}% | Prix: {price}")

            # DÉCLENCHEMENT RÉEL : SEUIL 70%
            if sentiment >= 70 and price:
                try:
                    send_sniper_signal(price, sentiment)
                    print("🎯 SIGNAL ENVOYÉ AUX VVIP")
                    time.sleep(14400) # Pause 4h pour éviter le sur-trading
                except Exception as e:
                    print(f"Erreur Telegram: {e}")
            
            time.sleep(900) # Analyse toutes les 15 minutes
        else:
            print("💤 Marché fermé.")
            time.sleep(3600)

if __name__ == "__main__":
    # Lancement du serveur Web en arrière-plan (pour Render Free)
    threading.Thread(target=run_flask).start()
    # Lancement de la boucle de trading
    trading_loop()
