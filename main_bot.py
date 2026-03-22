import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import MAIN_BOT_TOKEN
from database import bots

bot = telebot.TeleBot(MAIN_BOT_TOKEN, parse_mode="HTML")

# user step tracking
user_step = {}

# ==============================
# START
# ==============================
@bot.message_handler(commands=['start'])
def start(message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("➕ ADD BOT"),
        KeyboardButton("🤖 BOTS"),
        KeyboardButton("❌ REMOVE BOT")
    )

    bot.send_message(
        message.chat.id,
"""🤖 Welcome to Bot System

You can connect your own Telegram bot and turn it into a **TikTok downloader**.

📥 Features your bot will have:

• Download TikTok videos  
• Download TikTok photo slides  
• Work automatically for users  
• Ultra fast downloads  

⚙️ Setup Steps

1️⃣ Create bot via @BotFather  
2️⃣ Copy Bot Token  
3️⃣ Click ➕ Add Bot  
4️⃣ Send token  

🚀 Your bot will start automatically.""",
        reply_markup=kb
    )

# ==============================
# ADD BOT
# ==============================
@bot.message_handler(func=lambda m: m.text == "➕ ADD BOT")
def add_bot(message):
    bot.send_message(message.chat.id, "📥 Fadlan geli BOT TOKEN:")
    user_step[message.chat.id] = "waiting_token"

# ==============================
# HANDLE ALL
# ==============================
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    step = user_step.get(message.chat.id)

    # STEP 1: GET TOKEN
    if step == "waiting_token":
        token = message.text.strip()

        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("TikTok", "Instagram", "X")

        user_step[message.chat.id] = {"token": token}
        bot.send_message(
            message.chat.id,
            "🎯 Dooro platform botka:",
            reply_markup=kb
        )

    # STEP 2: SELECT PLATFORM
    elif isinstance(step, dict):
        platform = message.text
        token = step.get("token")

        bots.insert_one({
            "user_id": message.chat.id,
            "token": token,
            "platform": platform
        })

        bot.send_message(
            message.chat.id,
            f"✅ Bot waa la daray\n\n📌 Platform: {platform}"
        )

        user_step[message.chat.id] = None

# ==============================
# SHOW BOTS
# ==============================
@bot.message_handler(func=lambda m: m.text == "🤖 BOTS")
def show_bots(message):
    user_bots = bots.find({"user_id": message.chat.id})

    text = "🤖 Bots-kaaga:\n\n"
    count = 0

    for b in user_bots:
        count += 1
        text += f"{count}. {b['platform']} Bot\n"

    if count == 0:
        text = "❌ Wax bot ah ma lihid"

    bot.send_message(message.chat.id, text)

# ==============================
# REMOVE BOT
# ==============================
@bot.message_handler(func=lambda m: m.text == "❌ REMOVE BOT")
def remove_bot(message):
    user_bots = list(bots.find({"user_id": message.chat.id}))

    if not user_bots:
        bot.send_message(message.chat.id, "❌ Bot ma lihid")
        return

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    for i, b in enumerate(user_bots):
        kb.add(f"{i+1}. {b['platform']}")

    user_step[message.chat.id] = {
        "action": "remove",
        "bots": user_bots
    }

    bot.send_message(
        message.chat.id,
        "Dooro bot aad rabto inaad tirtirto:",
        reply_markup=kb
    )

@bot.message_handler(func=lambda m: True)
def remove_handler(message):
    step = user_step.get(message.chat.id)

    if isinstance(step, dict) and step.get("action") == "remove":
        try:
            index = int(message.text.split(".")[0]) - 1
            bot_data = step["bots"][index]

            bots.delete_one({"_id": bot_data["_id"]})

            bot.send_message(message.chat.id, "✅ Bot waa la tirtiray")
            user_step[message.chat.id] = None

        except:
            bot.send_message(message.chat.id, "❌ Qalad ayaa dhacay")

# ==============================
# RUN
# ==============================
print("Main bot is running...")
bot.infinity_polling()
