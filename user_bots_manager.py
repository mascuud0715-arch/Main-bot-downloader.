import telebot
import threading
import time

from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from database import get_all_bots, add_download, save_user_bot
from downloader import download_video
from receiver_bot import send_to_admin
from checker_bot import is_user_joined, force_join_message

# 🔥 tracking bots
running_bots = {}

# ==============================
# CLEAN TOKEN
# ==============================
def clean_token(token):
    return token.replace(" ", "").strip()

# ==============================
# BOT THREAD (AUTO RESTART)
# ==============================
def run_bot(bot):
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=60)
        except Exception as e:
            print("⚠️ Restarting bot...", e)
            time.sleep(5)

# ==============================
# START SINGLE BOT
# ==============================
def start_user_bot(token, platform):
    try:
        token = clean_token(token)

        if not token or ":" not in token:
            print("❌ Invalid token:", token)
            return

        # 🔥 avoid duplicate start
        if token in running_bots:
            return

        bot = telebot.TeleBot(token, parse_mode="HTML")
        running_bots[token] = bot

        print(f"🚀 Bot started: {token[:10]}")

        # ==============================
        # START COMMAND
        # ==============================
        @bot.message_handler(commands=['start'])
        def start(message):
            user_id = message.chat.id

            # 🔥 SAVE USER + BOT
            save_user_bot(user_id, token)

            if not is_user_joined(user_id):
                bot.send_message(user_id, force_join_message(user_id))
                return

            kb = ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add(KeyboardButton("🤖 Create your bot"))

            bot.send_message(
                user_id,
                f"👋 Send {platform} link to download video",
                reply_markup=kb
            )

        # ==============================
        # CREATE BOT BUTTON
        # ==============================
        @bot.message_handler(func=lambda m: m.text == "🤖 Create your bot")
        def create_bot(message):
            kb = InlineKeyboardMarkup()
            kb.add(
                InlineKeyboardButton(
                    "🤖 CREATE",
                    url="https://t.me/Create_Our_own_bot"
                )
            )

            bot.send_message(message.chat.id, "Click below 👇", reply_markup=kb)

        # ==============================
        # HANDLE ALL MESSAGES
        # ==============================
        @bot.message_handler(func=lambda m: True)
        def handle(message):
            user_id = message.chat.id
            url = message.text

            if not url:
                return

            # 🔥 SAVE USER AGAIN
            save_user_bot(user_id, token)

            if not is_user_joined(user_id):
                bot.send_message(user_id, force_join_message(user_id))
                return

            bot.send_chat_action(user_id, "typing")
            msg = bot.send_message(user_id, "⏳ Downloading...")

            try:
                res = download_video(url, platform)

                if res.get("status"):
                    video = res.get("video")

                    # delete loading msg
                    try:
                        bot.delete_message(user_id, msg.message_id)
                    except:
                        pass

                    bot.send_chat_action(user_id, "upload_video")

                    caption = f"Via: @{bot.get_me().username}"
                    bot.send_video(user_id, video, caption=caption)

                    bot.send_message(user_id, "Created: @Create_Our_own_bot")

                    # 🔥 download stats
                    add_download(platform)

                    # 🔥 send to admin
                    try:
                        send_to_admin(
                            video_url=video,
                            bot_name=bot.get_me().username,
                            username=message.from_user.username,
                            platform=platform
                        )
                    except Exception as e:
                        print("Receiver error:", e)

                else:
                    bot.delete_message(user_id, msg.message_id)
                    bot.send_message(user_id, "❌ Download failed")

            except Exception as e:
                print("ERROR:", e)

                try:
                    bot.delete_message(user_id, msg.message_id)
                except:
                    pass

                bot.send_message(user_id, "❌ Error occurred")

        # ==============================
        # START THREAD
        # ==============================
        thread = threading.Thread(target=run_bot, args=(bot,), daemon=True)
        thread.start()

    except Exception as e:
        print("❌ Start error:", e)

# ==============================
# START ALL BOTS
# ==============================
def start_all_bots():
    try:
        all_bots = get_all_bots()

        print(f"🤖 Loading {len(all_bots)} bots...")

        for b in all_bots:
            token = b.get("token")
            platform = b.get("platform")

            if token and platform:
                start_user_bot(token, platform)

    except Exception as e:
        print("❌ Load error:", e)
