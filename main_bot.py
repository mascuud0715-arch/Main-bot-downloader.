import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import MAIN_BOT_TOKEN
from database import bots

bot = telebot.TeleBot(MAIN_BOT_TOKEN, parse_mode="HTML")

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

Connect your own bot and turn it into a downloader.

📥 Features:
• TikTok downloader
• Instagram downloader
• X downloader
• Fast & automatic

⚙️ Steps:
1. Create bot via @BotFather
2. Copy token
3. Click ADD BOT
4. Done 🚀""",
        reply_markup=kb
    )

# ==============================
# ADD BOT
# ==============================
@bot.message_handler(func=lambda m: m.text == "➕ ADD BOT")
def add_bot(message):
    bot.send_message(message.chat.id, "📥 Send your BOT TOKEN:")
    user_step[message.chat.id] = "waiting_token"

# ==============================
# SHOW BOTS
# ==============================
@bot.message_handler(func=lambda m: m.text == "🤖 BOTS")
def show_bots(message):
    user_bots = list(bots.find({"user_id": message.chat.id}))

    if not user_bots:
        bot.send_message(message.chat.id, "❌ You have no bots")
        return

    text = "🤖 Your Bots:\n\n"

    for i, b in enumerate(user_bots, start=1):
        text += f"{i}. @{b.get('username')} ({b.get('platform')})\n"

    bot.send_message(message.chat.id, text)

# ==============================
# REMOVE BOT
# ==============================
@bot.message_handler(func=lambda m: m.text == "❌ REMOVE BOT")
def remove_bot(message):
    bot.send_message(message.chat.id, "❌ Send bot username (example: @mybot)")
    user_step[message.chat.id] = "remove_bot"

# ==============================
# HANDLE ALL STEPS
# ==============================
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    step = user_step.get(message.chat.id)

    # ======================
    # STEP 1: TOKEN
    # ======================
    if step == "waiting_token":
        token = message.text.strip()

        try:
            test_bot = telebot.TeleBot(token)
            me = test_bot.get_me()

            username = me.username

            user_step[message.chat.id] = {
                "token": token,
                "username": username
            }

            kb = ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add("TikTok", "Instagram", "X")

            bot.send_message(
                message.chat.id,
                f"🤖 Bot detected: @{username}\n\nSelect platform:",
                reply_markup=kb
            )

        except:
            bot.send_message(message.chat.id, "❌ Invalid token, try again")

    # ======================
    # STEP 2: PLATFORM
    # ======================
    elif isinstance(step, dict) and "token" in step:
        platform = message.text
        token = step["token"]
        username = step["username"]

        if platform not in ["TikTok", "Instagram", "X"]:
            bot.send_message(message.chat.id, "❌ Choose valid platform")
            return

        # save
        bots.insert_one({
            "user_id": message.chat.id,
            "token": token,
            "platform": platform,
            "username": username
        })

        bot.send_message(
            message.chat.id,
            f"""✅ Bot Added Successfully

🤖 Bot: @{username}
📱 Platform: {platform}

🚀 Your bot is now active!"""
        )

        user_step[message.chat.id] = None

    # ======================
    # REMOVE BOT STEP
    # ======================
    elif step == "remove_bot":
        username = message.text.replace("@", "").strip()

        result = bots.delete_one({
            "user_id": message.chat.id,
            "username": username
        })

        if result.deleted_count:
            bot.send_message(message.chat.id, f"✅ @{username} removed")
        else:
            bot.send_message(message.chat.id, "❌ Bot not found")

        user_step[message.chat.id] = None

# ==============================
# RUN
# ==============================
print("Main bot is running...")
bot.infinity_polling()
