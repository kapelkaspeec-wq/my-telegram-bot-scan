import os
import telebot
from google import genai

# Обновленный токен вашего Telegram-бота
TELEGRAM_TOKEN = "8955766364:AAF3V-vrTfjJVXEjzgWXUHnlxRUiH5rHWec"

# Ваш ключ API Gemini
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
        # Запрос к нейросети Gemini
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message.text,
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

if _name_ == "_main_":
    print("Бот успешно запущен!")
    bot.infinity_polling()
