import os
import time
import requests
import telebot
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

# VARIABLES D'ENVIRONNEMENT (Configurées sur Render)
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_KEY = os.getenv('TWELVE_DATA_TOKEN')

bot = telebot.TeleBot(TOKEN)
mada_tz = pytz.timezone('Indian/Antananarivo')

def get_live_sentiment():
    """Scraping MyFXBook pour le sentiment réel de l'Or"""
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
    """Prix réel XAU/USD via Twelve Data API"""
    try:
        url = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={API_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        return float(data['price'])
    except Exception as e:
        print(f"Erreur Prix TwelveData: {e}")
        return None

def is_market_open():
    now = datetime.now(mada_tz)
    # Marché fermé : Samedi et Dimanche jusqu'à 23h (Mada)
    if now.weekday() == 5 or (now.weekday() == 6 and now.hour < 23):
        return False
    return True

def send_sniper_signal(price, sentiment):
    """Envoi du signal réel uniquement"""
    tp = round(price + 15.0, 2)
    sl = round(price - 6.0, 2)
    msg = (
        f"🚀 **XAUUSD SNIPER VVIP** 🚀\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🎯 TYPE: **BUY NOW**\n"
        f"💰 ENTRY: {price}\n"
        f"✅ TP: {tp}\n"
        f"🛑 SL: {sl}\n"
        f"📊 ANALYSE: Sentiment {sentiment}% Short\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⌚ Heure Mada: {datetime.now(mada_tz).strftime('%H:%M')}\n"
        f"© VVIP Signal by Mc Anthonio"
    )
    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')

if __name__ == "__main__":
    print("🔥 MC ANTHONIO ENGINE : MODE ANALYSE RÉELLE DÉMARRÉ")
    while True:
        if is_market_open():
            sentiment = get_live_sentiment()
            price = get_live_price()
            
            # Log de surveillance dans Render
            current_time = datetime.now(mada_tz).strftime('%H:%M')
            print(f"[{current_time}] Sentiment: {sentiment}% | Prix: {price}")

            # DÉCLENCHEMENT : UNIQUEMENT SI SENTIMENT >= 70%
            if sentiment >= 70 and price:
                try:
                    send_sniper_signal(price, sentiment)
                    print("✅ SIGNAL DÉPLOYÉ SUR LE CANAL VVIP")
                    # On attend 4 heures avant de chercher le prochain signal
                    time.sleep(14400) 
            
            # Analyse toutes les 15 minutes
            time.sleep(900) 
        else:
            print("💤 Week-end : Marché fermé.")
            time.sleep(3600)
