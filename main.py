import requests
import os

# --- CONFIGURATION TEST ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
EMAIL = os.getenv("MYFXBOOK_EMAIL")
PASSWORD = os.getenv("MYFXBOOK_PASSWORD")

def test_connection():
    print("--- DÉBUT DU TEST SNIPER ---")
    
    # 1. Connexion Myfxbook
    login_url = f"https://api.myfxbook.com/api/login.json?email={EMAIL}&password={PASSWORD}"
    try:
        session_res = requests.get(login_url).json()
        session = session_res.get('session')
        if not session:
            print("❌ Erreur Myfxbook : Identifiants incorrects sur Render.")
            return
        print("✅ Session Myfxbook : OK")
        
        # 2. Récupération Data
        sent_url = f"https://api.myfxbook.com/api/get-community-outlook.json?session={session}"
        price_url = f"https://api.twelvedata.com/quote?symbol=XAU/USD&apikey={API_KEY}"
        
        sentiment = requests.get(sent_url).json()
        price_data = requests.get(price_url).json()
        
        short_pct = next(item['shortPercentage'] for item in sentiment['symbols'] if item['name'] == "XAUUSD")
        current_price = price_data['close']
        
        # 3. Envoi Telegram
        msg = (
            f"🧪 **TEST SYSTÈME RÉUSSI** 🧪\n"
            f"--------------------------\n"
            f"📡 Connexion API : ÉTABLIE\n"
            f"📊 Sentiment Or : {short_pct}%\n"
            f"💰 Prix Actuel : {current_price}\n"
            f"--------------------------\n"
            f"Le bot est prêt à chasser à 60%.\n"
            f"© Mc Anthonio Sniper VVIP"
        )
        
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
        print("✅ SIGNAL DE TEST ENVOYÉ SUR TELEGRAM !")
        
    except Exception as e:
        print(f"❌ Erreur technique : {e}")

if __name__ == "__main__":
    test_connection()
