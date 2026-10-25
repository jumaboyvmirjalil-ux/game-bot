import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot import types

# 1. Render talab qiladigan portni ochish uchun kichik veb-server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Veb-serverni alohida oqimda (thread) ishga tushiramiz
threading.Thread(target=run_server, daemon=True).start()

# 2. Telegram Bot qismi
TOKEN = os.environ.get("BOT_TOKEN") # Render'dagi Environment Variable'dan o'qiydi
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    web_app = types.WebAppInfo(url="https://yulduzcha-96x4.onrender.com")
    btn = types.InlineKeyboardButton(text="🎮 O'yinni O'ynash", web_app=web_app)
    buy_btn = types.InlineKeyboardButton(text="⭐ Yulduzcha sotib olish", callback_data="buy_stars")
    
    markup.add(btn)
    markup.add(buy_btn)
    
    bot.send_message(
        message.chat.id, 
        "Assalomu alaykum! Stars Mini App o'yiniga xush kelibsiz:", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "buy_stars")
def process_buy(call):
    prices = [types.LabeledPrice(label="10 ta Yulduzcha", amount=10)]
    
    bot.send_invoice(
        chat_id=call.message.chat.id,
        title="Yulduzchalar sotib olish",
        description="O'yin ichida ishlatish uchun 10 ta yulduzcha xarid qiling.",
        invoice_payload="stars-payload",
        provider_token="", 
        currency="XTR",     
        prices=prices,
        start_parameter="get_stars"
    )

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(
        message.chat.id, 
        "Tabriklayman! To'lov muvaffaqiyatli o'tdi. 🎉\nHisobingizga yulduzchalar qo'shildi!"
    )

# Botni ishga tushirish
bot.infinity_polling()