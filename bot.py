import os
import telebot
from openai import OpenAI
from docxtpl import DocxTemplate
from PIL import Image
import json
import threading
import base64
from http.server import BaseHTTPRequestHandler, HTTPServer

# Ваши рабочие ключи
TELEGRAM_TOKEN = "8870247392:AAH6YYzeFASFwynU4DaPLPC_AjdDswsXItg"
PROXY_API_KEY = "sk-heg3NF6rDU1VdDOMexnLkGriDfevyw0C"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Подключаемся к ProxyAPI
client = OpenAI(
    api_key=PROXY_API_KEY,
    base_url="https://api.proxyapi.ru/openai/v1"
)

TEMPLATE_PATH = "Бланк автоматической загрузки.docx"

# ==========================================
# ОБМАНКА ДЛЯ СЕРВЕРА RENDER
# ==========================================
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()
# ==========================================

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Бот готов! Пришлите фото заполненного бланка.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "⏳ Распознаю почерк и аккуратно заполняю бланк...")
    
    image_path = "temp_blank.jpg"
    fixed_image_path = "fixed_blank.jpg"
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(fixed_image_path, "JPEG")
        
        base64_image = encode_image(fixed_image_path)

        prompt = """
        Внимательно посмотри на этот рукописный бланк заказа. Извлеки все заполненные от руки данные.
        Верни результат СТРОГО в формате JSON. Ключи должны точно соответствовать полям на бланке: 
        номер_заказа, Дата_изготовления, ФИО_умершего, Дата_рождения, Дата_смерти, Обелиск, Тумба, Цветник_Надгробная, Портрет, Крест, Цветы, Свеча, Эпитафия, Сумма, Установка, Предоплата, Итог, Остаток, Адрес_кладбища, Телефон, ФИО_заказчика, Кем_принят_заказ, Дата_приема.
        Если какое-то поле не заполнено, оставь пустую строку "". Верни ТОЛЬКО чистый JSON, без лишнего текста.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        )
        
        text_response = response.choices[0].message.content.strip()
        
        if "{" in text_response and "}" in text_response:
            start = text_response.find("{")
            end = text_response.rfind("}") + 1
            text_response = text_response[start:end]
            
        data = json.loads(text_response)

        # --- ИДЕАЛЬНОЕ ЗАПОЛНЕНИЕ БЛАНКА ---
        doc = DocxTemplate(TEMPLATE_PATH)
        doc.render(data)
        
        output_filename = "Готовый_бланк.docx"
        doc.save(output_filename)

        with open(output_filename, 'rb') as doc_file:
            bot.send_document(message.chat.id, doc_file, caption="✅ Готово! Бланк идеально заполнен.")

    except Exception as e:
        bot.reply_to(message, f"❌ Произошла ошибка: {e}")
        print(f"ОШИБКА: {e}")
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)
        if os.path.exists(fixed_image_path):
            os.remove(fixed_image_path)

bot.infinity_polling()
