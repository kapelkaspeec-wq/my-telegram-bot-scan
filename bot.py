import os
import telebot
from google import genai
import threading
from flask import Flask

# Создаем легкое веб-приложение на Flask для Render
app = Flask(_name_)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Запускаем веб-сервер в фоне
threading.Thread(target=run_web, daemon=True).start()

# Токен и ключи
TELEGRAM_TOKEN = "8955766364:AAF3V-vrTfjJVXEjzgWXUHnlxRUiH5rHWec"
GEMINI_API_KEY = "AQ.Ab8RN6KZNjXJDUJTC-D0ojOlIAGlBjVWfTV2ARlFB6dbpycafg"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Бот успешно запущен на Render и готов к работе!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message.text,
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

if _name_ == "_main_":
    bot.infinity_polling()
