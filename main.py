import asyncio
import threading

import requests
from dotenv import load_dotenv
from flask import Flask

from emailing_file import PriceAlert  # Import handles email sending

app = Flask(__name__)

load_dotenv()
price_bot = PriceAlert()


# Function to get PI price in USD
def get_pi_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=pi-network&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return data.get("pi-network", {}).get("usd", None)


# Function to get USD to NGN exchange rate
def get_usd_to_ngn_rate():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    response = requests.get(url)
    data = response.json()
    return data.get("rates", {}).get("NGN", None)


# Convert PI price to Naira
async def convert_pi_to_naira():
    pi_price_usd = get_pi_price()
    exchange_rate = get_usd_to_ngn_rate()

    if pi_price_usd is not None and exchange_rate is not None:
        pi_price_ngn = pi_price_usd * exchange_rate
        return [pi_price_usd, round(pi_price_ngn, 2)]
    else:
        return "Conversion not available"


# Run email and Telegram alerts at intervals
async def send_alerts():
    while True:
        price_data = await convert_pi_to_naira()  # Wait for the conversion
        if isinstance(price_data, list):  # Ensure valid data before sending
            price_bot.send_email(price_data)
            await price_bot.send_telegram(price_data)

        print("✅ Alerts sent! Waiting for next interval...")

        await asyncio.sleep(3 * 60 * 60)  # Wait for 3 hours before next check


# Start the async task in a separate thread
def start_background_task():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_alerts())


@app.route('/')
def home():
    return "Bot is running!"


# Run the bot
if __name__ == "__main__":
    threading.Thread(target=start_background_task, daemon=True).start()  # Run in a separate thread
    app.run(host="0.0.0.0", port=10000)
