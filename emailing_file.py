import os
import smtplib
from email.message import EmailMessage

from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackContext


async def start_command(update: Update, context: CallbackContext):
    """Handles the /start command."""
    print("🚀 /start command received!")
    welcome_message = (
        "👋 *Welcome to the Pi Price Alert Bot!* 🚀\n\n"
        "This bot provides regular updates on the price of Pi Network (PI).\n\n"
        "✅ Price alerts are sent every 3 hours.\n"
        "📊 You'll receive both USD and NGN equivalent prices.\n"
        "💬 Just stay in this chat and wait for updates."
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


class PriceAlert:
    def __init__(self):
        self.EMAIL_ADDRESS = os.getenv('SENDER_EMAIL')
        self.EMAIL_PASSWORD = os.getenv('SECRET_KEY')
        self.RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')
        self.SENDER_NAME = os.getenv('SENDER_NAME')
        self.TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
        self.CHAT_ID = os.getenv('CHAT_ID')
        self.bot = Bot(token=self.TELEGRAM_TOKEN)

    def send_email(self, message):
        sender_email = self.EMAIL_ADDRESS
        sender_name = self.SENDER_NAME
        password = self.EMAIL_PASSWORD
        receiver_email = self.RECEIVER_EMAIL

        subject = f"Pi Network Price Update: ${message[0]}0"
        body = message

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender_name
        msg.set_content(f'''
                                    <!DOCTYPE html>
                                    <html lang="en">
                                    <head>
                                        <meta charset="UTF-8">
                                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                        <style>
                                            /* Add your custom CSS styles here */
                                            body {{
                                                font-family: Arial, sans-serif;
                                                background-color: #f7f7f7;
                                                margin: 0;
                                                padding: 0;
                                                text-align: center;
                                            }}

                                            .container {{
                                                max-width: 600px;
                                                margin: 0 auto;
                                                padding: 20px;
                                                background-color: #fff;
                                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                                border-radius: 5px;
                                            }}

                                            .header {{
                                                background-color: #333;
                                                color: #fff;
                                                text-align: center;
                                                padding: 20px 0;
                                            }}

                                            h1 {{
                                                color: #fff;
                                                font-size: 24px;
                                                margin-top: 10px;
                                            }}

                                            p {{
                                                color: #666;
                                                font-size: 16px;
                                                line-height: 1.5;
                                            }}

                                            .cta-button {{
                                                display: inline-block;
                                                background-color: #000;
                                                color: #fff;
                                                font-size: 18px;
                                                padding: 10px 20px;
                                                text-decoration: none;
                                                border-radius: 5px;
                                            }}
                                        </style>
                                    </head>
                                    <body>
                                        <div style="text-align: center;" class="container">
                                            <div class="header">
                                                <h1>Current Pi Price</h1>
                                            </div>
                                            <p style="text-align: center;">The current price of PI is ${body[0]}</p>
                                            <p style="text-align: center;">Pi price in NGN: ₦{body[1]}</p>
                                            <a style="text-align: center;" href="https://coinmarketcap.com/currencies/pi/" class="cta-button">Check out here</a>
                                            <footer style="margin-top: 20px;">
                                                <hr style="top: 10px; border: none; height: 1px; background-color: grey;">
                                                <p style="text-align: center; margin-top: 25px; font-size: 12px; font-style: italic;">© Copyright 2025 DELMAR BOT. All rights reserved.</p>
                                                <p style="text-align: center; padding-top: 20px; font-size: 10px;">Want to change how you receive these emails?</p>
                                                <p style="text-align: center; font-size: 12px;">You can <a href='https://www.google.com/'>update your preferences</a> or <a href='https://www.google.com/'>unsubscribe</a>.</p>
                                            </footer>
                                        </div>
                                    </body>
                                    </html>
                                ''', subtype='html')

        msg["To"] = receiver_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)

    async def send_telegram(self, message):
        await self.bot.send_message(chat_id=self.CHAT_ID,
                                    text=f"Good day,\n\nThe current price of PI is ${message[0]}\nPi price in NGN: ₦{message[1]}")

    def run_telegram_bot(self):
        """Starts the bot and listens for messages."""
        print("✅ Telegram bot is running...")
        app = Application.builder().token(self.TELEGRAM_TOKEN).build()

        # Add command handlers
        app.add_handler(CommandHandler("start", start_command))

        # Start polling
        app.run_polling()
