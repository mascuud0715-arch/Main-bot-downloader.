import telebot
from config import RECEIVER_BOT_TOKEN, ADMIN_ID

# ==============================
# BOT
# ==============================
bot = telebot.TeleBot(RECEIVER_BOT_TOKEN, parse_mode="HTML")

# ==============================
# SEND VIDEO TO ADMIN
# ==============================
def send_to_admin(video_url, bot_name, username, platform):
    try:
        caption = f"""
📥 <b>New Download</b>

🤖 Bot: @{bot_name}
👤 User: @{username if username else 'NoUsername'}
📱 Platform: {platform}
"""

        bot.send_video(
            ADMIN_ID,
            video_url,
            caption=caption
        )

    except Exception as e:
        print("❌ Receiver error:", e)

# ==============================
# OPTIONAL: START COMMAND (DEBUG)
# ==============================
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "✅ Receiver Bot Active")

# ==============================
# RUN (OPTIONAL haddii aad rabto standalone)
# ==============================
def run_receiver():
    print("📥 Receiver bot running...")

    try:
        bot.remove_webhook()
    except:
        pass
