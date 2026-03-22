import telebot
from config import RECEIVER_BOT_TOKEN, ADMIN_ID
from database import get_setting

bot = telebot.TeleBot(RECEIVER_BOT_TOKEN, parse_mode="HTML")

# ==============================
# SEND VIDEO TO ADMIN
# ==============================
def send_to_admin(video_url, bot_name, username, platform):
    # check if receiver is ON
    status = get_setting("receiver_status", "OFF")

    if status != "ON":
        return

    caption = f"""
📥 New Download

🤖 Bot: {bot_name}
👤 User: @{username if username else 'NoUsername'}
📱 Platform: {platform}

Created: @Create_Our_own_bot
"""

    try:
        bot.send_video(
            ADMIN_ID,
            video_url,
            caption=caption
        )
    except Exception as e:
        print("Receiver error:", e)

# ==============================
# TEST COMMAND
# ==============================
@bot.message_handler(commands=['test'])
def test(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "✅ Receiver bot is working")

# ==============================
# RUN
# ==============================
print("Receiver bot running...")
bot.infinity_polling()
