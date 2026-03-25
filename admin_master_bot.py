import os
import telebot
import threading
import time
from datetime import datetime

from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)

from run_all import running_bots, bot_tokens
from database import get_users_by_token, get_all_users_global

# ==============================
# ENV
# ==============================
TOKEN = os.getenv("ADMIN_MASTER_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ==============================
# STORAGE
# ==============================
user_step = {}
scheduled_posts = []

# 🔓 OPEN / 🔒 CLOSE SYSTEM
SYSTEM_MODE = "open"  # open / close

# ==============================
# MENU
# ==============================
def admin_menu(chat_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add(
        KeyboardButton("🌍 Post All"),
        KeyboardButton("📢 Broadcast Users")
    )

    kb.add(
        KeyboardButton("🎯 Post Single"),
        KeyboardButton("⏰ Schedule")
    )

    kb.add(
        KeyboardButton("🔓 Open System"),
        KeyboardButton("🔒 Close System")
    )

    kb.add(
        KeyboardButton("📊 Stats")
    )

    bot.send_message(chat_id, "👑 <b>ADMIN PANEL</b>", reply_markup=kb)

# ==============================
# START
# ==============================
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != ADMIN_ID:
        return

    admin_menu(message.chat.id)

# ==============================
# OPEN SYSTEM
# ==============================
@bot.message_handler(func=lambda m: m.text == "🔓 Open System")
def open_sys(message):
    global SYSTEM_MODE
    SYSTEM_MODE = "open"
    bot.send_message(message.chat.id, "✅ System OPEN")

# ==============================
# CLOSE SYSTEM
# ==============================
@bot.message_handler(func=lambda m: m.text == "🔒 Close System")
def close_sys(message):
    global SYSTEM_MODE
    SYSTEM_MODE = "close"
    bot.send_message(message.chat.id, "✅ System CLOSED")

# ==============================
# POST ALL
# ==============================
@bot.message_handler(func=lambda m: m.text == "🌍 Post All")
def post_all(message):
    user_step[message.chat.id] = "all"
    bot.send_message(message.chat.id, "📤 Send post:")

# ==============================
# BROADCAST USERS
# ==============================
@bot.message_handler(func=lambda m: m.text == "📢 Broadcast Users")
def bc_users(message):
    user_step[message.chat.id] = "users"
    bot.send_message(message.chat.id, "✉️ Send message:")

# ==============================
# SINGLE POST
# ==============================
@bot.message_handler(func=lambda m: m.text == "🎯 Post Single")
def single(message):
    user_step[message.chat.id] = "single_1"
    bot.send_message(message.chat.id, "📥 Send @channel or group id:")

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
        f"""📊 SYSTEM

Bots: {len(running_bots)}
Users: {len(get_all_users_global())}
Mode: {SYSTEM_MODE}
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

    # 🌍 POST ALL GROUPS + CHANNELS
    if step == "all":
        for username, b in running_bots.items():
            try:
                b.send_message(ADMIN_ID, "🚀 Sending...")
                send_to_all_chats(b, message)
            except:
                pass

        done(message)

    # 📢 USERS
    elif step == "users":
        users = get_all_users_global()

        for u in users:
            try:
                send_any(bot, u, message)
            except:
                pass

        done(message)

    # 🎯 SINGLE STEP 1
    elif step == "single_1":
        user_step[message.chat.id] = {"target": message.text}
        bot.send_message(message.chat.id, "📤 Send content:")

    # 🎯 SINGLE STEP 2
    elif isinstance(step, dict) and "target" in step:
        target = step["target"]

        for b in running_bots.values():
            try:
                send_any(b, target, message)
            except:
                pass

        done(message)

    # ⏰ TIME STEP 1
    elif step == "time":
        user_step[message.chat.id] = {"time": message.text}
        bot.send_message(message.chat.id, "📤 Send content:")

    # ⏰ SAVE SCHEDULE
    elif isinstance(step, dict) and "time" in step:
        scheduled_posts.append({
            "time": step["time"],
            "message": message
        })

        bot.send_message(message.chat.id, "✅ Scheduled")
        user_step[message.chat.id] = None
        admin_menu(message.chat.id)

# ==============================
# SEND ALL GROUPS/CHANNELS
# ==============================
def send_to_all_chats(bot_obj, message):
    try:
        updates = bot_obj.get_updates(limit=100)

        chat_ids = set()

        for u in updates:
            if u.message:
                chat_ids.add(u.message.chat.id)

        for cid in chat_ids:
            try:
                send_any(bot_obj, cid, message)
            except:
                pass
    except:
        pass

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
                        send_to_all_chats(b, post["message"])
                    except:
                        pass

                post["sent"] = True

        time.sleep(30)

threading.Thread(target=scheduler, daemon=True).start()

# ==============================
# RUN
# ==============================
print("👑 ADMIN MASTER PRO RUNNING...")
bot.infinity_polling(skip_pending=True)
