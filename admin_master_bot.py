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
# MEMORY
# ==============================
user_step = {}
scheduled_posts = []

# ==============================
# MENU
# ==============================
def admin_menu(chat_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("📢 Broadcast"),
        KeyboardButton("📡 Post All Channels")
    )
    kb.add(
        KeyboardButton("👥 Post All Groups"),
        KeyboardButton("🎯 Single Channel Post")
    )
    kb.add(
        KeyboardButton("📊 View Channels"),
        KeyboardButton("📊 View Groups")
    )

    bot.send_message(chat_id, "👑 <b>ADMIN PANEL</b>", reply_markup=kb)

# ==============================
# START
# ==============================
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "❌ Admin only")

    admin_menu(message.chat.id)

# ==============================
# BROADCAST
# ==============================
@bot.message_handler(func=lambda m: m.text == "📢 Broadcast")
def broadcast(message):
    user_step[message.chat.id] = "broadcast"
    bot.send_message(message.chat.id, "✉️ Send message to broadcast:")

# ==============================
# POST ALL CHANNELS
# ==============================
@bot.message_handler(func=lambda m: m.text == "📡 Post All Channels")
def post_channels(message):
    user_step[message.chat.id] = "post_channels"
    bot.send_message(message.chat.id, "📤 Send post (text/photo/video):")

# ==============================
# POST ALL GROUPS
# ==============================
@bot.message_handler(func=lambda m: m.text == "👥 Post All Groups")
def post_groups(message):
    user_step[message.chat.id] = "post_groups"
    bot.send_message(message.chat.id, "📤 Send post for groups:")

# ==============================
# SINGLE CHANNEL
# ==============================
@bot.message_handler(func=lambda m: m.text == "🎯 Single Channel Post")
def single_channel(message):
    user_step[message.chat.id] = "single_channel"
    bot.send_message(message.chat.id, "📥 Send channel username (e.g @channel):")

# ==============================
# VIEW CHANNELS / GROUPS
# ==============================
@bot.message_handler(func=lambda m: m.text == "📊 View Channels")
def view_channels(message):
    bot.send_message(message.chat.id, "📡 Channels list feature (connect DB here)")

@bot.message_handler(func=lambda m: m.text == "📊 View Groups")
def view_groups(message):
    bot.send_message(message.chat.id, "👥 Groups list feature (connect DB here)")

# ==============================
# HANDLE
# ==============================
@bot.message_handler(content_types=['text', 'photo', 'video'])
def handle(message):
    if message.chat.id != ADMIN_ID:
        return

    step = user_step.get(message.chat.id)

    # ======================
    # BROADCAST
    # ======================
    if step == "broadcast":
        text = message.text

        # 👉 halkan ku dar DB users
        users = []  # get from DB

        for u in users:
            try:
                bot.send_message(u, text)
            except:
                pass

        bot.send_message(message.chat.id, "✅ Broadcast sent")
        user_step[message.chat.id] = None
        admin_menu(message.chat.id)

    # ======================
    # POST ALL CHANNELS
    # ======================
    elif step == "post_channels":
        channels = []  # 👉 kasoo qaad DB

        for ch in channels:
            try:
                if message.photo:
                    bot.send_photo(ch, message.photo[-1].file_id, caption=message.caption)
                elif message.video:
                    bot.send_video(ch, message.video.file_id, caption=message.caption)
                else:
                    bot.send_message(ch, message.text)
            except:
                pass

        bot.send_message(message.chat.id, "✅ Posted to all channels")
        user_step[message.chat.id] = None
        admin_menu(message.chat.id)

    # ======================
    # POST ALL GROUPS
    # ======================
    elif step == "post_groups":
        groups = []  # 👉 kasoo qaad DB

        for g in groups:
            try:
                bot.send_message(g, message.text)
            except:
                pass

        bot.send_message(message.chat.id, "✅ Posted to all groups")
        user_step[message.chat.id] = None
        admin_menu(message.chat.id)

    # ======================
    # SINGLE CHANNEL STEP 1
    # ======================
    elif step == "single_channel":
        user_step[message.chat.id] = {
            "channel": message.text
        }
        bot.send_message(message.chat.id, "📤 Send content now:")

    # ======================
    # SINGLE CHANNEL STEP 2
    # ======================
    elif isinstance(step, dict):
        channel = step["channel"]

        try:
            if message.photo:
                bot.send_photo(channel, message.photo[-1].file_id, caption=message.caption)
            elif message.video:
                bot.send_video(channel, message.video.file_id, caption=message.caption)
            else:
                bot.send_message(channel, message.text)

            bot.send_message(message.chat.id, "✅ Posted successfully")

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {e}")

        user_step[message.chat.id] = None
        admin_menu(message.chat.id)

# ==============================
# SCHEDULER (AUTO POST)
# ==============================
def scheduler():
    while True:
        now = datetime.now().strftime("%H:%M")

        for post in scheduled_posts:
            if post["time"] == now and not post.get("sent"):
                try:
                    bot.send_message(post["chat_id"], post["text"])
                    post["sent"] = True
                except:
                    pass

        time.sleep(30)

threading.Thread(target=scheduler, daemon=True).start()

# ==============================
# RUN
# ==============================
print("👑 ADMIN MASTER BOT RUNNING...")
