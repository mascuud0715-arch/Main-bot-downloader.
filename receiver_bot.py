import telebot
from config import RECEIVER_BOT_TOKEN, ADMIN_ID
from database import get_setting

bot = telebot.TeleBot(RECEIVER_BOT_TOKEN, parse_mode="HTML")


def send_to_admin(video_url, bot_name, username, platform):
    try:
        # 🔥 CHECK RECEIVER STATUS
        if get_setting("receiver_status") != "ON":
            return

        caption = f"""
📥 <b>New Download</b>

🤖 Bot: @{bot_name}
👤 User: @{username}
📱 Platform: {platform}
"""

        # VIDEO
        if hasattr(video_url, "read"):
            bot.send_video(ADMIN_ID, video_url, caption=caption)

        # haddii string la diray (old)
        else:
            bot.send_message(ADMIN_ID, caption + "\n⚠️ No file")

    except Exception as e:
        print("RECEIVER ERROR:", e)
