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
BOT_USERNAME = os.getenv("BOT_USERNAME")  # without @

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ==============================
# STORAGE
# ==============================
user_step = {}
users = set()
groups = set()
channels = set()
scheduled_posts = []

# ==============================
# MENU
# ==============================
def admin_menu(chat_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("📢 Broadcast"),
        KeyboardButton("📡 Post Channels")
    )
    kb.add(
        KeyboardButton("👥 Post Groups"),
        KeyboardButton("🎯 Single Channel")
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
        # USER VIEW (ADD BUTTONS)
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton(
                "➕ Add me to Group",
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
            )
        )

        bot.send_message(
            message.chat.id,
            "🤖 Add me to your group to use downloader 🔥",
            reply_markup=kb
        )
        return

    admin_menu(message.chat.id)

# ==============================
# AUTO DETECT GROUPS / CHANNELS
# ==============================
@bot.message_handler(content_types=['new_chat_members'])
def added(message):
    if message.chat.type in ["group", "supergroup"]:
        groups.add(message.chat.id)

# channels
@bot.channel_post_handler(func=lambda m: True)
def channel_detect(message):
    channels.add(message.chat.id)

# save users
@bot.message_handler(func=lambda m: True)
def save_user(message):
    if message.chat.type == "private":
        users.add(message.chat.id)

# ==============================
# BROADCAST
# ==============================
@bot.message_handler(func=lambda m: m.text == "📢 Broadcast")
def bc(message):
    user_step[message.chat.id] = "bc"
    bot.send_message(message.chat.id, "✉️ Send message:")

# ==============================
# POST CHANNELS
# ==============================
@bot.message_handler(func=lambda m: m.text == "📡 Post Channels")
def pc(message):
    user_step[message.chat.id] = "pc"
    bot.send_message(message.chat.id, "📤 Send post:")

# ==============================
# POST GROUPS
# ==============================
@bot.message_handler(func=lambda m: m.text == "👥 Post Groups")
def pg(message):
    user_step[message.chat.id] = "pg"
    bot.send_message(message.chat.id, "📤 Send post:")

# ==============================
# SINGLE CHANNEL
# ==============================
@bot.message_handler(func=lambda m: m.text == "🎯 Single Channel")
def sc(message):
    user_step[message.chat.id] = "sc"
    bot.send_message(message.chat.id, "📥 Send @channel:")

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
        f"""📊 Stats

Users: {len(users)}
Groups: {len(groups)}
Channels: {len(channels)}"""
    )

# ==============================
# HANDLE
# ==============================
@bot.message_handler(content_types=['text', 'photo', 'video'])
def handle(message):
    if message.chat.id != ADMIN_ID:
        return

    step = user_step.get(message.chat.id)

    # BROADCAST
    if step == "bc":
        for u in users:
            send_any(u, message)

        bot.send_message(message.chat.id, "✅ Done")
        user_step[message.chat.id] = None
        admin_menu(message.chat.id)

    # CHANNELS
    elif step == "pc":
        for ch in channels:
            send_any(ch, message)

        bot.send_message(message.chat.id, "✅ Channels done")
        user_step[message.chat.id] = None
        admin_menu(message.chat.id)

    # GROUPS
    elif step == "pg":
        for g in groups:
            send_any(g, message)

        bot.send_message(message.chat.id, "✅ Groups done")
        user_step[message.chat.id] = None
        admin_menu(message.chat.id)

    # SINGLE STEP 1
    elif step == "sc":
        user_step[message.chat.id] = {"channel": message.text}
        bot.send_message(message.chat.id, "📤 Send content:")

    # SINGLE STEP 2
    elif isinstance(step, dict) and "channel" in step:
        send_any(step["channel"], message)

        bot.send_message(message.chat.id, "✅ Sent")
        user_step[message.chat.id] = None
        admin_menu(message.chat.id)

    # TIME
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
def send_any(chat_id, message):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            "➕ Add me to Group",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
        )
    )

    if message.photo:
        bot.send_photo(chat_id, message.photo[-1].file_id,
                       caption=message.caption, reply_markup=kb)

    elif message.video:
        bot.send_video(chat_id, message.video.file_id,
                       caption=message.caption, reply_markup=kb)

    else:
        bot.send_message(chat_id, message.text, reply_markup=kb)

# ==============================
# SCHEDULER
# ==============================
def scheduler():
    while True:
        now = datetime.now().strftime("%H:%M")

        for post in scheduled_posts:
            if post["time"] == now and not post.get("sent"):

                for u in users:
                    send_any(u, post["message"])

                post["sent"] = True

        time.sleep(30)

threading.Thread(target=scheduler, daemon=True).start()

# ==============================
# RUN
# ==============================
print("👑 ADMIN MASTER BOT RUNNING...")
