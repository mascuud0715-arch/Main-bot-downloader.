import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==============================
# ENV VARIABLES
# ==============================
SUPPORT_BOT_TOKEN = os.getenv("SUPPORT_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

if not SUPPORT_BOT_TOKEN:
    raise Exception("❌ SUPPORT_BOT_TOKEN not set")

if not ADMIN_ID:
    raise Exception("❌ ADMIN_ID not set")

bot = telebot.TeleBot(SUPPORT_BOT_TOKEN, parse_mode="HTML")


# ==============================
# START
# ==============================
@bot.message_handler(commands=['start'])
def start(message):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📥 Video Error", callback_data="video"),
        InlineKeyboardButton("⚠️ Download Error", callback_data="download")
    )
    kb.add(
        InlineKeyboardButton("📢 Broadcast Error", callback_data="broadcast"),
        InlineKeyboardButton("⚙️ System Error", callback_data="system")
    )

    bot.send_message(
        message.chat.id,
        "🤖 Welcome to Support Bot\nChoose your problem 👇",
        reply_markup=kb
    )


# ==============================
# BUTTON HANDLER
# ==============================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    data = call.data
    bot.answer_callback_query(call.id)

    if data == "video":
        bot.send_message(call.message.chat.id, "📹 Send video / link")
        bot.register_next_step_handler(call.message, forward_to_admin, "VIDEO")

    elif data == "download":
        bot.send_message(call.message.chat.id, "⚠️ Send download problem")
        bot.register_next_step_handler(call.message, auto_fix_download)

    elif data == "broadcast":
        bot.send_message(call.message.chat.id, "📢 Send broadcast issue")
        bot.register_next_step_handler(call.message, auto_fix_broadcast)

    elif data == "system":
        bot.send_message(call.message.chat.id, "⚙️ Send system error")
        bot.register_next_step_handler(call.message, auto_fix_system)


# ==============================
# AUTO FIX
# ==============================
def auto_fix_download(message):
    text = (message.text or "").lower()

    if "tiktok" in text:
        bot.send_message(message.chat.id, "✅ Fix: TikTok link must be public")

    elif "x" in text or "twitter" in text:
        bot.send_message(message.chat.id, "✅ Fix: Use correct X link")

    else:
        forward_to_admin(message, "DOWNLOAD")


def auto_fix_broadcast(message):
    bot.send_message(
        message.chat.id,
        "✅ Fix:\n- Users exist\n- Token sax yahay\n- Restart bot"
    )


def auto_fix_system(message):
    bot.send_message(
        message.chat.id,
        "✅ Railway Fix:\n1. Restart service\n2. Check logs\n3. Check MONGO_URI"
    )


# ==============================
# FORWARD TO ADMIN
# ==============================
def forward_to_admin(message, problem_type):
    try:
        user = message.from_user

        text = f"""
🚨 NEW SUPPORT REQUEST

👤 User: @{user.username}
🆔 ID: {user.id}
📌 Type: {problem_type}

💬 Message:
{message.text}
"""

        bot.send_message(ADMIN_ID, text)

        # haddii video / photo jiro
        if message.video:
            bot.send_video(ADMIN_ID, message.video.file_id)

        if message.photo:
            bot.send_photo(ADMIN_ID, message.photo[-1].file_id)

        bot.send_message(message.chat.id, "✅ Sent to admin")

    except Exception as e:
        print("Forward error:", e)
        bot.send_message(message.chat.id, "❌ Failed to send")


# ==============================
# RUN
# ==============================
def run():
    print("🤖 Support bot running...")
    bot.infinity_polling(skip_pending=True)
