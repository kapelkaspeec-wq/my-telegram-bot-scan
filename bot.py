import os
import telebot
from google import genai
from flask import Flask, request

# Токен и ключи
TELEGRAM_TOKEN = "8955766364:AAF3V-vrTfjJVXEjzgWXUHnlxRUiH5rHWec"
GEMINI_API_KEY = "AQ.Ab8RN6KZNjXJDUJTC-D0ojOlIAGlBjVWfTV2ARlFB6dbpycafg"

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
ai_client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(_name_)

# Ссылка на ваш сервис на Render (мы заменим её на вашу точную ссылку)
# Формат: https://< имя-вашего-сервиса >.onrender.com
RENDER_URL = "https://my-telegram-bot-scan.onrender.com"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        return "Forbidden", 403

@app.route("/")
def index():
    return "Bot is running via Webhook!", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Бот успешно запущен на Render через Webhook!")

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
    # Убираем старый вебхук и привязываем новый
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{TELEGRAM_TOKEN}")
    
    # Запускаем Flask на порту, который требует Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
