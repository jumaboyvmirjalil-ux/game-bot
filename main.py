import telebot
from telebot import types

# Bot tokeningizni shu yerga yozasiz
TOKEN = "8931423972:AAEmhYQLent9bH4HV9GYyfWOSV5Sojyu03g"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Foydalanuvchiga salom beramiz va Mini App ochadigan tugma yasaymiz
    markup = types.InlineKeyboardMarkup()
    
    # Bizning Render'dan olgan havolamiz:
    web_app = types.WebAppInfo(url="https://yulduzcha-96x4.onrender.com")
    
    # Tugma yaratish
    btn = types.InlineKeyboardButton(text="🎮 O'yinni O'ynash", web_app=web_app)
    markup.add(btn)
    
    bot.send_message(
        message.chat.id, 
        "Assalomu alaykum! Stars Mini App o'yiniga xush kelibsiz. O'ynash uchun pastdagi tugmani bosing:", 
        reply_markup=markup
    )

# Botni ishga tushirish
bot.infinity_polling()