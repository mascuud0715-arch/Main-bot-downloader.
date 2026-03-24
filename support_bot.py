import telebot
import os

# ==============================
# ENV TOKEN (RAILWAY)
# ==============================
TOKEN = os.getenv("SUPPORT_BOT_TOKEN")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ==============================
# START MENU
# ==============================
def support_menu():
    from telebot.types import ReplyKeyboardMarkup, KeyboardButton

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("🎥 Video Download Error"),
        KeyboardButton("🤖 Bot No Talk")
    )
    return kb


# ==============================
# START
# ==============================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🛠 Welcome to Support Bot\n\nChoose problem 👇",
        reply_markup=support_menu()
    )


# ==============================
# ERROR TYPES
# ==============================
@bot.message_handler(func=lambda m: m.text == "🎥 Video Download Error")
def video_error(message):
    msg = bot.send_message(
        message.chat.id,
        "📥 Send your bot username (@yourbot):"
    )
    bot.register_next_step_handler(msg, fix_bot)


@bot.message_handler(func=lambda m: m.text == "🤖 Bot No Talk")
def bot_dead(message):
    msg = bot.send_message(
        message.chat.id,
        "📥 Send your bot username (@yourbot):"
    )
    bot.register_next_step_handler(msg, fix_bot)


# ==============================
# FIX BOT (SIMPLE VERSION)
# ==============================
def fix_bot(message):
    username = message.text.replace("@", "").lower()

    bot.send_message(
        message.chat.id,
        f"✅ Bot @{username} received!\n\n⏳ We will fix it soon."
    )

    # 👉 Halkan waxaad ku dari kartaa:
    # - send_to_admin()
    # - restart bot
    # - check status


# ==============================
# RUN
# ==============================
def run():
    print("🛠 Support Bot Running...")
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    run()
