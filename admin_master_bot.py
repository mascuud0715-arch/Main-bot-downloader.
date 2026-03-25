import os
import telebot
import threading
import time
from datetime import datetime

from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# ==============================
# ENV
# ==============================
TOKEN = os.getenv("ADMIN_MASTER_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ==============================
# IMPORT SYSTEM
# ==============================
from database import get_all_users_global
from run_all import running_bots, bot_tokens

# ==============================
# STORAGE
# ==============================
user_step = {}
scheduled_posts = []

# ==============================
# MENU
# ==============================
def admin_menu(chat_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add(
        KeyboardButton("📢 Broadcast Users"),
        KeyboardButton("📡 Broadcast Channels")
    )

    kb.add(
        KeyboardButton("👥 Broadcast Groups"),
        KeyboardButton("🌍 Global Broadcast")
    )

    kb.add(
        KeyboardButton("⏰ Schedule"),
        KeyboardButton("📊 Stats")
    )

    bot.send_message(chat_id, "👑 <b>ADMIN PANEL</b>", reply_markup=kb)

# ==============================
# START
# ==============================
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Not allowed")
        return

    admin_menu(message.chat.id)

# ==============================
# BROADCAST USERS
# ==============================
@bot.message_handler(func=lambda m: m.text == "📢 Broadcast Users")
def bc_users(message):
    user_step[message.chat.id] = "users"
    bot.send_message(message.chat.id, "✉️ Send message:")

# ==============================
# BROADCAST CHANNELS
# ==============================
@bot.message_handler(func=lambda m: m.text == "📡 Broadcast Channels")
def bc_channels(message):
    user_step[message.chat.id] = "channels"
    bot.send_message(message.chat.id, "📤 Send message:")

# ==============================
# BROADCAST GROUPS
# ==============================
@bot.message_handler(func=lambda m: m.text == "👥 Broadcast Groups")
def bc_groups(message):
    user_step[message.chat.id] = "groups"
    bot.send_message(message.chat.id, "📤 Send message:")

# ==============================
# GLOBAL BROADCAST (ALL BOTS)
# ==============================
@bot.message_handler(func=lambda m: m.text == "🌍 Global Broadcast")
def global_bc(message):
    user_step[message.chat.id] = "global"
    bot.send_message(message.chat.id, "🌍 Send message to ALL bots:")

# ==============================
# SCHEDULE
# ==============================
@bot.message_handler(func=lambda m: m.text == "⏰ Schedule")
def schedule(message):
    user_step[message.chat.id] = "time"
    bot.send_message(message.chat.id, "⏰ Send time HH:MM")

# ==============================
# STATS
# ==============================
@bot.message_handler(func=lambda m: m.text == "📊 Stats")
def stats(message):
    bot.send_message(
        message.chat.id,
        f"""📊 SYSTEM STATS

Running Bots: {len(running_bots)}
Users: {len(get_all_users_global())}
"""
    )

# ==============================
# HANDLE
# ==============================
@bot.message_handler(content_types=['text', 'photo', 'video'])
def handle(message):
    if message.chat.id != ADMIN_ID:
        return

    step = user_step.get(message.chat.id)

    # USERS
    if step == "users":
        users = get_all_users_global()

        for u in users:
            try:
                send_any(bot, u, message)
            except:
                pass

        done(message)

    # CHANNELS
    elif step == "channels":
        for b in running_bots.values():
            try:
                b.send_message("@yourchannel", message.text)
            except:
                pass

        done(message)

    # GROUPS
    elif step == "groups":
        for b in running_bots.values():
            try:
                b.send_message(-1001234567890, message.text)
            except:
                pass

        done(message)

    # GLOBAL
    elif step == "global":
        for username, b in running_bots.items():
            users = get_users_by_token(bot_tokens[username])

            for u in users:
                try:
                    send_any(b, u, message)
                except:
                    pass

        done(message)

    # TIME STEP 1
    elif step == "time":
        user_step[message.chat.id] = {"time": message.text}
        bot.send_message(message.chat.id, "📤 Send content:")

    # SAVE SCHEDULE
    elif isinstance(step, dict) and "time" in step:
        scheduled_posts.append({
            "time": step["time"],
            "message": message
        })

        bot.send_message(message.chat.id, "✅ Scheduled")
        user_step[message.chat.id] = None
        admin_menu(message.chat.id)

# ==============================
# SEND FUNCTION
# ==============================
def send_any(bot_obj, chat_id, message):
    if message.photo:
        bot_obj.send_photo(chat_id, message.photo[-1].file_id,
                           caption=message.caption)

    elif message.video:
        bot_obj.send_video(chat_id, message.video.file_id,
                           caption=message.caption)

    else:
        bot_obj.send_message(chat_id, message.text)

# ==============================
# DONE
# ==============================
def done(message):
    bot.send_message(message.chat.id, "✅ Done")
    user_step[message.chat.id] = None
    admin_menu(message.chat.id)

# ==============================
# SCHEDULER
# ==============================
def scheduler():
    while True:
        now = datetime.now().strftime("%H:%M")

        for post in scheduled_posts:
            if post["time"] == now and not post.get("sent"):

                for b in running_bots.values():
                    try:
                        send_any(b, ADMIN_ID, post["message"])
                    except:
                        pass

                post["sent"] = True

        time.sleep(30)

threading.Thread(target=scheduler, daemon=True).start()

# ==============================
# RUN
# ==============================
print("👑 ADMIN MASTER RUNNING...")
bot.infinity_polling(skip_pending=True)
