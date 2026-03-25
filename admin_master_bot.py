import os
import telebot
import threading
import time
from datetime import datetime

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from run_all import running_bots, start_all_bots
from database import get_all_users_global

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
media_buffer = {}

SYSTEM_MODE = "open"

# ==============================
# MENU
# ==============================
def admin_menu(chat_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("🌍 Post All", "🎯 Post Single")
    kb.add("📢 Broadcast Users", "📊 Stats")
    kb.add("⏰ Schedule Post", "🖼 Schedule 40 Images")
    kb.add("🧹 Clear Schedule", "🔁 Restart Bots")
    kb.add("🔓 Open System", "🔒 Close System")

    bot.send_message(chat_id, "👑 <b>ADMIN PANEL PRO MAX</b>", reply_markup=kb)

# ==============================
# START
# ==============================
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != ADMIN_ID:
        return
    admin_menu(message.chat.id)

# ==============================
# SYSTEM MODE
# ==============================
@bot.message_handler(func=lambda m: m.text == "🔓 Open System")
def open_sys(message):
    global SYSTEM_MODE
    SYSTEM_MODE = "open"
    bot.send_message(message.chat.id, "✅ System OPEN")

@bot.message_handler(func=lambda m: m.text == "🔒 Close System")
def close_sys(message):
    global SYSTEM_MODE
    SYSTEM_MODE = "close"
    bot.send_message(message.chat.id, "⛔ System CLOSED")

# ==============================
# POST ALL
# ==============================
@bot.message_handler(func=lambda m: m.text == "🌍 Post All")
def post_all(message):
    user_step[message.chat.id] = "post_all"
    bot.send_message(message.chat.id, "📤 Send post now")

# ==============================
# POST SINGLE
# ==============================
@bot.message_handler(func=lambda m: m.text == "🎯 Post Single")
def single(message):
    user_step[message.chat.id] = "single_target"
    bot.send_message(message.chat.id, "📥 Send @channel or group id")

# ==============================
# BROADCAST USERS
# ==============================
@bot.message_handler(func=lambda m: m.text == "📢 Broadcast Users")
def broadcast_users(message):
    user_step[message.chat.id] = "broadcast"
    bot.send_message(message.chat.id, "✉️ Send message")

# ==============================
# SCHEDULE POST
# ==============================
@bot.message_handler(func=lambda m: m.text == "⏰ Schedule Post")
def schedule_post(message):
    user_step[message.chat.id] = "schedule_target"
    bot.send_message(message.chat.id, "📥 Send @channel or group id")

# ==============================
# SCHEDULE 40 IMAGES
# ==============================
@bot.message_handler(func=lambda m: m.text == "🖼 Schedule 40 Images")
def schedule_images(message):
    user_step[message.chat.id] = "img_target"
    bot.send_message(message.chat.id, "📥 Send @channel or group id")

# ==============================
# CLEAR SCHEDULE
# ==============================
@bot.message_handler(func=lambda m: m.text == "🧹 Clear Schedule")
def clear_schedule(message):
    scheduled_posts.clear()
    bot.send_message(message.chat.id, "🧹 Cleared all scheduled posts")

# ==============================
# RESTART BOTS
# ==============================
@bot.message_handler(func=lambda m: m.text == "🔁 Restart Bots")
def restart(message):
    start_all_bots()
    bot.send_message(message.chat.id, "♻️ Bots restarted")

# ==============================
# STATS
# ==============================
@bot.message_handler(func=lambda m: m.text == "📊 Stats")
def stats(message):
    bot.send_message(message.chat.id,
        f"📊 Bots: {len(running_bots)}\nUsers: {len(get_all_users_global())}\nMode: {SYSTEM_MODE}"
    )

# ==============================
# HANDLE
# ==============================
@bot.message_handler(content_types=['text', 'photo'])
def handle(message):
    if message.chat.id != ADMIN_ID:
        return

    step = user_step.get(message.chat.id)

    # ================= POST ALL =================
    if step == "post_all":
        for b in running_bots.values():
            chat_ids = get_admin_chats(b)

            for cid in chat_ids:
                try:
                    send_any(b, cid, message)
                except:
                    pass

        done(message)

    # ================= BROADCAST =================
    elif step == "broadcast":
        for u in get_all_users_global():
            try:
                send_any(bot, u, message)
            except:
                pass
        done(message)

    # ================= SINGLE =================
    elif step == "single_target":
        user_step[message.chat.id] = {"target": message.text}
        bot.send_message(message.chat.id, "📤 Send content")

    elif isinstance(step, dict) and "target" in step:
        for b in running_bots.values():
            try:
                send_any(b, step["target"], message)
            except:
                pass
        done(message)

    # ================= SCHEDULE =================
    elif step == "schedule_target":
        user_step[message.chat.id] = {"target": message.text}
        bot.send_message(message.chat.id, "⏰ Send time HH:MM")

    elif isinstance(step, dict) and "target" in step and "time" not in step:
        step["time"] = message.text
        user_step[message.chat.id] = step
        bot.send_message(message.chat.id, "📤 Send content")

    elif isinstance(step, dict) and "time" in step:
        scheduled_posts.append({
            "type": "single",
            "target": step["target"],
            "time": step["time"],
            "message": message
        })
        bot.send_message(message.chat.id, "✅ Scheduled")
        done(message)

    # ================= 40 IMAGES =================
    elif step == "img_target":
        media_buffer.clear()
        user_step[message.chat.id] = {"img_target": message.text}
        bot.send_message(message.chat.id, "⏰ Send time HH:MM")

    elif isinstance(step, dict) and "img_target" in step and "time" not in step:
        step["time"] = message.text
        media_buffer["photos"] = []
        bot.send_message(message.chat.id, "🖼 Send up to 40 images")

    elif isinstance(step, dict) and "img_target" in step and message.photo:
        media_buffer["photos"].append(message.photo[-1].file_id)

        if len(media_buffer["photos"]) >= 40:
            scheduled_posts.append({
                "type": "images",
                "target": step["img_target"],
                "time": step["time"],
                "photos": media_buffer["photos"]
            })
            bot.send_message(message.chat.id, "✅ 40 Images Scheduled")
            done(message)

# ==============================
# GET ADMIN CHATS
# ==============================
def get_admin_chats(bot_obj):
    chats = []
    try:
        updates = bot_obj.get_updates(limit=200)
        for u in updates:
            if u.message:
                if u.message.chat.type in ["group", "supergroup", "channel"]:
                    chats.append(u.message.chat.id)
    except:
        pass
    return list(set(chats))

# ==============================
# SEND
# ==============================
def send_any(bot_obj, chat_id, message):
    if message.photo:
        bot_obj.send_photo(chat_id, message.photo[-1].file_id, caption=message.caption)
    else:
        bot_obj.send_message(chat_id, message.text)

# ==============================
# DONE
# ==============================
def done(message):
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

                if post["type"] == "single":
                    for b in running_bots.values():
                        try:
                            send_any(b, post["target"], post["message"])
                        except:
                            pass

                elif post["type"] == "images":
                    for img in post["photos"]:
                        for b in running_bots.values():
                            try:
                                b.send_photo(post["target"], img)
                                time.sleep(2)
                            except:
                                pass

                post["sent"] = True

        time.sleep(20)

threading.Thread(target=scheduler, daemon=True).start()

# ==============================
# RUN
# ==============================
print("👑 ADMIN MASTER PRO MAX RUNNING...")
