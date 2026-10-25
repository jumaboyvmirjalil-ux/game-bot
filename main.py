import telebot
from telebot import types

# Botingiz API Tokeni
TOKEN = "8931423972:AAEmhYQLent9bH4HV9GYyfWOSV5Sojyu03g"
bot = telebot.TeleBot(TOKEN)

# Foydalanuvchilar ma'lumotlarini saqlash uchun bazaviy lug'at (Real loyihada ma'lumotlar bazasi shart)
# Struktura: user_id: {"stars": 0, "level": 1, "tasks": {}}
users_db = {}

# /start buyrug'i - Telegram akkauntga bog'lash va Asosiy Menyu
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name

    # Agar foydalanuvchi birinchi marta kirsa, bazaga qo'shamiz
    if user_id not in users_db:
        users_db[user_id] = {
            "name": user_name,
            "stars": 50,      # Boshlang'ich sovg'a yulduzcha
            "level": 1,       # Boshlang'ich bosqich
            "withdrawing": False
        }

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton("⭐ Mening Balansim")
    item2 = types.KeyboardButton("🎮 O'yin / Bosqichlar")
    item3 = types.KeyboardButton("📋 Kunlik Vazifalar")
    item4 = types.KeyboardButton("💸 Yulduzchalarni Yechish (1000⭐)")
    markup.add(item1, item2, item3, item4)

    bot.send_message(
        user_id,
        f"Assalomu alaykum, **{user_name}**! 🌟\n"
        f"Telegram Stars o'yin botiga xush kelibsiz. Akkauntingiz muvaffaqiyatli ulandi!\n\n"
        f"Quyidagi menyudan kerakli bo'limni tanlang:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# Menyularni boshqarish
@bot.message_handler(content_types=['text'])
def bot_message(message):
    user_id = message.chat.id

    if user_id not in users_db:
        users_db[user_id] = {"name": message.from_user.first_name, "stars": 50, "level": 1}

    user_data = users_db[user_id]

    if message.text == "⭐ Mening Balansim":
        bot.send_message(
            user_id,
            f"👤 Foydalanuvchi: {user_data['name']}\n"
            f"⭐ Yulduzchalar: **{user_data['stars']} ta**\n"
            f"🏆 Joriy Bosqich: **{user_data['level']}-bosqich**",
            parse_mode="Markdown"
        )

    elif message.text == "🎮 O'yin / Bosqichlar":
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton(f"🚀 1-Bosqich (Tikish: 10⭐)", callback_data="play_level_1")
        btn2 = types.InlineKeyboardButton(f"🚀 2-Bosqich (Tikish: 25⭐)", callback_data="play_level_2")
        btn3 = types.InlineKeyboardButton(f"🚀 3-Bosqich (Tikish: 50⭐)", callback_data="play_level_3")
        markup.add(btn1, btn2, btn3)

        bot.send_message(
            user_id,
            "🎮 **O'yin Bosqichlari:**\n"
            "Har bir bosqichda ma'lum miqdorda yulduzcha tikib o'ynaysiz. Yutsangiz yulduzchangiz ikki barobar ko'payadi va keyingi bosqichga o'tasiz!",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif message.text == "📋 Kunlik Vazifalar":
        markup = types.InlineKeyboardMarkup()
        btn_task1 = types.InlineKeyboardButton("✅ Kanalga obuna bo'lish (+20⭐)", callback_data="task_channel")
        btn_task2 = types.InlineKeyboardButton("✅ Do'stni taklif qilish (+50⭐)", callback_data="task_ref")
        markup.add(btn_task1, btn_task2)

        bot.send_message(
            user_id,
            "📋 **Kunlik Vazifalar:**\nQuyidagi vazifalarni bajarib bepul yulduzchalar yig'ing:",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif message.text == "💸 Yulduzchalarni Yechish (1000⭐)":
        current_stars = user_data['stars']
        if current_stars >= 1000:
            bot.send_message(
                user_id,
                "🎉 Tabriklaymiz! Siz 1,000 ta yulduzcha yig'dingiz.\n"
                "Yulduzchalarni Telegram hisobingizga yoki hamyoningizga yechib olish uchun admin bilan bog'laning: @Admin_Username"
            )
        else:
            needed = 1000 - current_stars
            bot.send_message(
                user_id,
                f"⚠️ Hozirgi balansingiz: **{current_stars} ta** yulduzcha.\n"
                f"Yechib olish uchun yana **{needed} ta** yulduzcha yetishmaydi. Maqsadga erishish uchun o'ynang va vazifalarni bajaring! 💪",
                parse_mode="Markdown"
            )

# Tugmalar va O'yin jarayonini boshqarish (Callback)
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.message.chat.id
    if user_id not in users_db:
        users_db[user_id] = {"name": call.from_user.first_name, "stars": 50, "level": 1}

    user_data = users_db[user_id]

    # O'yin bosqichlari logikasi
    if call.data.startswith("play_level_"):
        level_num = int(call.data.split("_")[-1])
        cost = 10 if level_num == 1 else (25 if level_num == 2 else 50)

        if user_data['stars'] >= cost:
            user_data['stars'] -= cost  # Tikish uchun yechib olamiz
            
            # O'yin sharti (Misol uchun: 50% yutish ehtimoli)
            import random
            is_win = random.choice([True, False])

            if is_win:
                reward = cost * 2
                user_data['stars'] += reward
                user_data['level'] = max(user_data['level'], level_num + 1)
                bot.answer_callback_query(call.id, f"🏆 G'alaba! Siz {reward} ta yulduzcha yutib oldingiz!")
                bot.edit_message_text(
                    chat_id=user_id,
                    message_id=call.message.message_id,
                    text=f"🎉 Tabriklaymiz! {level_num}-bosqichni muvaffaqiyatli yakunladingiz va yutib oldingiz!\n⭐ Joriy balans: {user_data['stars']} ta"
                )
            else:
                bot.answer_callback_query(call.id, "😔 Afsuski, yutqazdingiz. Qaytadan urinib ko'ring!")
                bot.edit_message_text(
                    chat_id=user_id,
                    message_id=call.message.message_id,
                    text=f"❌ {level_num}-bosqichda omad kelmadi ({cost}⭐ yutqazdingiz).\n⭐ Joriy balans: {user_data['stars']} ta"
                )
        else:
            bot.answer_callback_query(call.id, "⚠️ Hisobingizda yulduzchalar yetarli emas!", show_alert=True)

    # Kunlik vazifalar logikasi
    elif call.data == "task_channel":
        user_data['stars'] += 20
        bot.answer_callback_query(call.id, "+20 ta yulduzcha qo'shildi! 🎉")
        bot.send_message(user_id, f"✅ Vazifa bajarildi! Hisobingizga 20 ta yulduzcha qo'shildi. Jami: {user_data['stars']}⭐")

    elif call.data == "task_ref":
        user_data['stars'] += 50
        bot.answer_callback_query(call.id, "+50 ta yulduzcha qo'shildi! 🚀")
        bot.send_message(user_id, f"✅ Do'st taklif qilish vazifasi bajarildi! 50 ta yulduzcha qo'shildi. Jami: {user_data['stars']}⭐")

# Botni ishga tushirish
bot.polling(none_stop=True)