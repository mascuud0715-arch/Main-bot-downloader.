import telebot
import threading
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from config import MAIN_BOT_TOKEN
from database import bots
from user_bots_manager import start_user_bot

bot = telebot.TeleBot(MAIN_BOT_TOKEN, parse_mode="HTML")

user_step = {}

# ==============================
# MAIN MENU FUNCTION
# ==============================
def main_menu(chat_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("➕ ADD BOT"),
        KeyboardButton("🤖 BOTS")
    )
    kb.add(KeyboardButton("❌ REMOVE BOT"))

    bot.send_message(
        chat_id,
"""🤖 Welcome to Bot System

📥 Features:
• TikTok downloader
• Instagram downloader
• X downloader

⚙️ Steps:
1. Create bot via @BotFather
2. Copy token
3. Click ADD BOT
4. Done 🚀""",
        reply_markup=kb
    )

# ==============================
# START
# ==============================
@bot.message_handler(commands=['start'])
def start(message):
    main_menu(message.chat.id)

# ==============================
# ADD BOT
# ==============================
@bot.message_handler(func=lambda m: m.text == "➕ ADD BOT")
def add_bot(message):
    bot.send_message(message.chat.id, "📥 Send your BOT TOKEN from @BotFather :")
    user_step[message.chat.id] = "waiting_token"

# ==============================
# SHOW BOTS
# ==============================
@bot.message_handler(func=lambda m: m.text == "🤖 BOTS")
def show_bots(message):
    user_bots = list(bots.find({"user_id": message.chat.id}))

    if not user_bots:
        bot.send_message(message.chat.id, "❌ You don't have any bots")
        return

    text = "🤖 Your Bots:\n\n"
    for i, b in enumerate(user_bots, start=1):
        username = b.get("username", "Unknown")
        platform = b.get("platform", "Unknown")

        text += f"{i}. @{username} ({platform})\n"

    bot.send_message(message.chat.id, text)

# ==============================
# REMOVE BOT
# ==============================
@bot.message_handler(func=lambda m: m.text == "❌ REMOVE BOT")
def remove_bot(message):
    bot.send_message(message.chat.id, "❌ Send bot username (example: @mybot)")
    user_step[message.chat.id] = "remove_bot"

# ==============================
# HANDLE ALL
# ==============================
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    step = user_step.get(message.chat.id)

    # ======================
    # TOKEN STEP
    # ======================
    if step == "waiting_token":
        token = message.text.strip()

        if ":" not in token:
            bot.send_message(message.chat.id, "❌ Invalid token format")
            return

        try:
            test_bot = telebot.TeleBot(token)
            me = test_bot.get_me()

            username = me.username

            user_step[message.chat.id] = {
                "token": token,
                "username": username
            }

            kb = ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add(
                KeyboardButton("TikTok"),
                KeyboardButton("Instagram"),
                KeyboardButton("X")
            )

            bot.send_message(
                message.chat.id,
                f"🤖 Bot detected: @{username}\n\nSelect platform:",
                reply_markup=kb
            )

        except Exception as e:
            print("TOKEN ERROR:", e)
            bot.send_message(message.chat.id, "❌ Invalid token")

    # ======================
    # PLATFORM STEP
    # ======================
    elif isinstance(step, dict):
        platform = message.text
        token = step["token"]
        username = step["username"]

        if platform not in ["TikTok", "Instagram", "X"]:
            bot.send_message(message.chat.id, "❌ Choose valid platform")
            return

        existing = bots.find_one({"token": token})
        if existing:
            bot.send_message(message.chat.id, "⚠️ Bot already exists")
            user_step[message.chat.id] = None
            main_menu(message.chat.id)
            return

        # SAVE DB
        bots.insert_one({
            "user_id": message.chat.id,
            "token": token,
            "platform": platform,
            "username": username
        })

        # 🔥 START BOT (THREAD FIXED)
        def run_bot():
            try:
                start_user_bot(token, platform)
            except Exception as e:
                print("START BOT ERROR:", e)

        threading.Thread(target=run_bot).start()

        bot.send_message(
            message.chat.id,
            f"""✅ Bot Added Successfully

🤖 Bot: @{username}
📱 Platform: {platform}

🚀 Your bot is LIVE!"""
        )

        user_step[message.chat.id] = None

        # 🔥 BACK TO MENU
        main_menu(message.chat.id)

    # ======================
    # REMOVE STEP
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
        main_menu(message.chat.id)

    print("🚀 Main bot running...")
    bot.infinity_polling(skip_pending=True)
