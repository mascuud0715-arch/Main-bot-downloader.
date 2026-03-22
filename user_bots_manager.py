import telebot
import threading
from database import get_all_bots
from downloader import download_video
from receiver_bot import send_to_admin
from checker_bot import is_user_joined, force_join_message
from database import add_download

# ==============================
# STORE RUNNING BOTS
# ==============================
running_bots = {}

# ==============================
# START SINGLE BOT
# ==============================
def start_user_bot(token, platform):
    if token in running_bots:
        return

    bot = telebot.TeleBot(token, parse_mode="HTML")
    running_bots[token] = bot

    # ==============================
    # START COMMAND
    # ==============================
    @bot.message_handler(commands=['start'])
    def start(message):
        user_id = message.chat.id

        # force join check
        if not is_user_joined(user_id):
            bot.send_message(user_id, force_join_message(user_id))
            return

        bot.send_message(
            user_id,
            f"👋 Send {platform} link to download video"
        )

    # ==============================
    # HANDLE LINKS
    # ==============================
    @bot.message_handler(func=lambda m: True)
    def handle(message):
        user_id = message.chat.id
        url = message.text

        # check join again
        if not is_user_joined(user_id):
            bot.send_message(user_id, force_join_message(user_id))
            return

        bot.send_message(user_id, "⏳ Downloading...")

        res = download_video(url, platform)

        if res["status"]:
            video = res["video"]

            caption = f"""
Via: @{bot.get_me().username}

Created: @Create_Our_own_bot
"""

            try:
                bot.send_video(user_id, video, caption=caption)

                # save stats
                add_download(user_id, platform)

                # send to admin (receiver)
                send_to_admin(
                    video_url=video,
                    bot_name=bot.get_me().username,
                    username=message.from_user.username,
                    platform=platform
                )

            except Exception as e:
                bot.send_message(user_id, "❌ Failed to send video")

        else:
            bot.send_message(user_id, "❌ Download failed")

    print(f"Started bot: {token}")

    bot.infinity_polling()

# ==============================
# START ALL BOTS
# ==============================
def start_all_bots():
    bots = get_all_bots()

    for b in bots:
        token = b.get("token")
        platform = b.get("platform")

        thread = threading.Thread(
            target=start_user_bot,
            args=(token, platform)
        )

        thread.start()
