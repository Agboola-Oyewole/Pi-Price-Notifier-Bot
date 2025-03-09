import asyncio
import threading

import requests
from dotenv import load_dotenv
from flask import Flask

from emailing_file import PriceAlert  # Import handles email sending

app = Flask(__name__)

load_dotenv()
price_bot = PriceAlert()


def get_pi_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=pi-network&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return data.get("pi-network", {}).get("usd", None)


def get_usd_to_ngn_rate():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    response = requests.get(url)
    data = response.json()
    return data.get("rates", {}).get("NGN", None)


async def convert_pi_to_naira():
    pi_price_usd = get_pi_price()
    exchange_rate = get_usd_to_ngn_rate()

    if pi_price_usd is not None and exchange_rate is not None:
        pi_price_ngn = pi_price_usd * exchange_rate
        return [pi_price_usd, round(pi_price_ngn, 2)]
    else:
        return "Conversion not available"


async def send_alerts():
    price_data = await convert_pi_to_naira()
    if isinstance(price_data, list):
        price_bot.send_email(price_data)
        await price_bot.send_telegram(price_data)
    print("✅ Alerts sent!")


@app.route('/run-alerts')
def run_alerts():
    asyncio.run(send_alerts())
    return "Alerts sent!"


@app.route('/ping')
def ping():
    return "I'm alive!", 200


if __name__ == "__main__":
    async def main():
        # Run Telegram bot
        await price_bot.run_telegram_bot()  # Ensure this function is async


    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000), daemon=True)
    flask_thread.start()

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(main())  # Run bot as an async task in existing event loop
    except RuntimeError:
        asyncio.run(main())  # Start new event loop only if none is running
