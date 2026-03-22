import telebot
from telebot.types import ReplyKeyboardMarkup
from config import ADMIN_BOT_TOKEN, ADMIN_ID
from database import (
    set_setting,
    get_setting,
    get_all_users,
    get_all_bots,
    get_download_count,
    get_platform_stats,
    channels
)

bot = telebot.TeleBot(ADMIN_BOT_TOKEN, parse_mode="HTML")

# ==============================
# ADMIN CHECK
# ==============================
def is_admin(user_id):
    return user_id == ADMIN_ID

# ==============================
# CHANNEL FUNCTIONS
# ==============================
def add_new_channel(channel_id):
    if not channels.find_one({"channel_id": channel_id}):
        channels.insert_one({"channel_id": channel_id})

def list_channels():
    chs = list(channels.find())

    if not chs:
        return "❌ No channels added"

    text = "📋 Channels List:\n\n"
    for i, ch in enumerate(chs, start=1):
        text += f"{i}. {ch.get('channel_id')}\n"

    return text

def clear_all_channels():
    channels.delete_many({})
    return "✅ All channels removed"

# ==============================
# START PANEL
# ==============================
@bot.message_handler(commands=['start'])
def admin_panel(message):
    if not is_admin(message.chat.id):
        return

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🟢 System ON", "🔴 System OFF")
    kb.add("📥 Receiver ON", "📤 Receiver OFF")
    kb.add("📢 Broadcast")
    kb.add("➕ Add Channel", "📋 Channels")
    kb.add("❌ Clear Channels")
    kb.add("📊 Stats")

    bot.send_message(message.chat.id, "⚙️ <b>Admin Panel</b>", reply_markup=kb)

# ==============================
# SYSTEM CONTROL
# ==============================
@bot.message_handler(func=lambda m: m.text == "🟢 System ON")
def system_on(message):
    if not is_admin(message.chat.id): return
    set_setting("system_status", "ON")
    bot.send_message(message.chat.id, "✅ System is ON")

@bot.message_handler(func=lambda m: m.text == "🔴 System OFF")
def system_off(message):
    if not is_admin(message.chat.id): return
    set_setting("system_status", "OFF")
    bot.send_message(message.chat.id, "⛔ System is OFF")

# ==============================
# RECEIVER CONTROL
# ==============================
@bot.message_handler(func=lambda m: m.text == "📥 Receiver ON")
def receiver_on(message):
    if not is_admin(message.chat.id): return
    set_setting("receiver_status", "ON")
    bot.send_message(message.chat.id, "📥 Receiver ON")

@bot.message_handler(func=lambda m: m.text == "📤 Receiver OFF")
def receiver_off(message):
    if not is_admin(message.chat.id): return
    set_setting("receiver_status", "OFF")
    bot.send_message(message.chat.id, "📤 Receiver OFF")

# ==============================
# BROADCAST (🔥 PRO VERSION)
# ==============================
@bot.message_handler(func=lambda m: m.text == "📢 Broadcast")
def broadcast_start(message):
    if not is_admin(message.chat.id): return

    msg = bot.send_message(
        message.chat.id,
        "📢 Send message / photo / video to broadcast"
    )
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    if not is_admin(message.chat.id): return

    users = get_all_users()
    success = 0
    fail = 0

    for user in users:
        uid = user.get("user_id")

        try:
            # TEXT
            if message.text:
                bot.send_message(uid, message.text)

            # PHOTO
            elif message.photo:
                bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption)

            # VIDEO
            elif message.video:
                bot.send_video(uid, message.video.file_id, caption=message.caption)

            # FORWARD
            else:
                bot.forward_message(uid, message.chat.id, message.message_id)

            success += 1

        except Exception as e:
            fail += 1

    bot.send_message(
        message.chat.id,
        f"✅ Sent: {success}\n❌ Failed: {fail}"
    )

# ==============================
# ADD CHANNEL
# ==============================
@bot.message_handler(func=lambda m: m.text == "➕ Add Channel")
def add_channel_handler(message):
    if not is_admin(message.chat.id): return

    msg = bot.send_message(message.chat.id, "Send channel username (e.g: @mychannel)")
    bot.register_next_step_handler(msg, save_channel)

def save_channel(message):
    if not is_admin(message.chat.id): return

    ch = message.text.strip()

    if not ch.startswith("@"):
        bot.send_message(message.chat.id, "❌ Must start with @")
        return

    add_new_channel(ch)
    bot.send_message(message.chat.id, "✅ Channel added")

# ==============================
# CHANNELS
# ==============================
@bot.message_handler(func=lambda m: m.text == "📋 Channels")
def show_channels(message):
    if not is_admin(message.chat.id): return
    bot.send_message(message.chat.id, list_channels())

# ==============================
# CLEAR CHANNELS
# ==============================
@bot.message_handler(func=lambda m: m.text == "❌ Clear Channels")
def clear_channels_handler(message):
    if not is_admin(message.chat.id): return
    bot.send_message(message.chat.id, clear_all_channels())

# ==============================
# STATS
# ==============================
@bot.message_handler(func=lambda m: m.text == "📊 Stats")
def stats(message):
    if not is_admin(message.chat.id): return

    total_users = len(get_all_users())
    total_bots = len(get_all_bots())
    total_downloads = get_download_count()

    platform_stats = get_platform_stats()

    text = f"""
📊 <b>System Stats</b>

👥 Users: {total_users}
🤖 Bots: {total_bots}
📥 Downloads: {total_downloads}

📱 Platforms:
"""

    for p in platform_stats:
        text += f"{p['_id']}: {p['count']}\n"

    bot.send_message(message.chat.id, text)

# ==============================
# RUN
# ==============================
print("🛠 Admin bot running...")
bot.infinity_polling(skip_pending=True)
