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
# CHANNEL FUNCTIONS (INTEGRATED)
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

def clear_channels():
    channels.delete_many({})
    return "✅ All channels removed"

# ==============================
# START PANEL
# ==============================
@bot.message_handler(commands=['start'])
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        return

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🟢 System ON", "🔴 System OFF")
    kb.add("📥 Receiver ON", "📤 Receiver OFF")
    kb.add("➕ Add Channel", "📋 Channels")
    kb.add("❌ Clear Channels")
    kb.add("📊 Stats")

    bot.send_message(message.chat.id, "⚙️ Admin Control Panel", reply_markup=kb)

# ==============================
# SYSTEM CONTROL
# ==============================
@bot.message_handler(func=lambda m: m.text == "🟢 System ON")
def system_on(message):
    if message.chat.id != ADMIN_ID:
        return

    set_setting("system_status", "ON")
    bot.send_message(message.chat.id, "✅ System is ON")

@bot.message_handler(func=lambda m: m.text == "🔴 System OFF")
def system_off(message):
    if message.chat.id != ADMIN_ID:
        return

    set_setting("system_status", "OFF")
    bot.send_message(message.chat.id, "⛔ System is OFF")

# ==============================
# RECEIVER CONTROL
# ==============================
@bot.message_handler(func=lambda m: m.text == "📥 Receiver ON")
def receiver_on(message):
    if message.chat.id != ADMIN_ID:
        return

    set_setting("receiver_status", "ON")
    bot.send_message(message.chat.id, "📥 Receiver ON")

@bot.message_handler(func=lambda m: m.text == "📤 Receiver OFF")
def receiver_off(message):
    if message.chat.id != ADMIN_ID:
        return

    set_setting("receiver_status", "OFF")
    bot.send_message(message.chat.id, "📤 Receiver OFF")

# ==============================
# ADD CHANNEL
# ==============================
@bot.message_handler(func=lambda m: m.text == "➕ Add Channel")
def add_channel_handler(message):
    if message.chat.id != ADMIN_ID:
        return

    bot.send_message(message.chat.id, "Send channel username (e.g: @mychannel)")
    bot.register_next_step_handler(message, save_channel)

def save_channel(message):
    if message.chat.id != ADMIN_ID:
        return

    channel_id = message.text.strip()
    add_new_channel(channel_id)

    bot.send_message(message.chat.id, "✅ Channel added")

# ==============================
# SHOW CHANNELS
# ==============================
@bot.message_handler(func=lambda m: m.text == "📋 Channels")
def show_channels(message):
    if message.chat.id != ADMIN_ID:
        return

    bot.send_message(message.chat.id, list_channels())

# ==============================
# CLEAR CHANNELS
# ==============================
@bot.message_handler(func=lambda m: m.text == "❌ Clear Channels")
def clear_channels_handler(message):
    if message.chat.id != ADMIN_ID:
        return

    bot.send_message(message.chat.id, clear_channels())

# ==============================
# STATS
# ==============================
@bot.message_handler(func=lambda m: m.text == "📊 Stats")
def stats(message):
    if message.chat.id != ADMIN_ID:
        return

    users = len(get_all_users())
    bots_count = len(get_all_bots())
    downloads = get_download_count()

    platform_stats = get_platform_stats()

    text = f"""
📊 System Stats

👥 Users: {users}
🤖 Bots: {bots_count}
📥 Downloads: {downloads}

📱 Platform Stats:
"""

    for p in platform_stats:
        text += f"{p['_id']}: {p['count']}\n"

    bot.send_message(message.chat.id, text)

# ==============================
# RUN
# ==============================
print("Admin bot running...")
