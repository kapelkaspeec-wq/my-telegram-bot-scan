import os
import telebot
from google import genai
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Настройка веб-сервера для Render (чтобы хостинг видел активность и не выключал сервис)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Запускаем веб-сервер в отдельном потоке, чтобы он не мешал боту
threading.Thread(target=run_web_server, daemon=True).start()

# Токен Telegram-бота
TELEGRAM_TOKEN = "8955766364:AAF3V-vrTfjJVXEjzgWXUHnlxRUiH5rHWec"

# Ключ API Gemini
GEMINI_API_KEY = "AQ.Ab8RN6KZNjXJDUJTC-D0ojOlIAGlBjVWfTV2ARlFB6dbpycafg"

# Инициализация клиентов
bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот на базе Gemini. Напиши мне любой вопрос или задачу!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message.text,
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

if _name_ == "_main_":
    print("Бот и веб-сервер успешно запущены!")
    bot.infinity_polling()
