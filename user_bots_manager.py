import telebot
import threading
import time

from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from database import (
    get_all_bots,
    add_download,
    add_user,
    get_setting
)

from downloader import download_video
from receiver_bot import send_to_admin
from checker_bot import is_user_joined, force_join_message

# ==============================
# STORE RUNNING BOTS
# ==============================
running_bots = {}

# ==============================
# SAFE RUNNER (ANTI-CRASH)
# ==============================
def run_bot(bot, name):
    print(f"🚀 Running: {name}")

    while True:
        try:
            bot.infinity_polling(
                skip_pending=True,
                timeout=60,
                long_polling_timeout=60
            )
        except Exception as e:
            print(f"❌ {name} crashed:", e)
            time.sleep(5)

# ==============================
# START SINGLE BOT
# ==============================
def start_user_bot(token, platform):
    try:
        token = token.strip()

        # ❌ invalid token
        if not token or ":" not in token:
            print("❌ Invalid token:", token)
            return

        # ❌ duplicate protection (IMPORTANT 🔥)
        if token in running_bots:
            print("⚠️ Already running:", token[:10])
            return

        bot = telebot.TeleBot(token, parse_mode="HTML")

        # 🔥 VERY IMPORTANT (fix 409 error)
        try:
            bot.remove_webhook()
        except:
            pass

        running_bots[token] = bot

        print(f"✅ Bot started: {token[:10]}")

        # ==============================
        # START COMMAND
        # ==============================
        @bot.message_handler(commands=['start'])
        def start(message):
            user_id = message.chat.id

            # ✅ SAVE USER
            add_user(user_id)

            # ❌ SYSTEM OFF
            if get_setting("system_status") == "OFF":
                bot.send_message(user_id, "⛔ Bot is currently OFF")
                return

            # ❌ FORCE JOIN
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

            # ❌ SYSTEM OFF
            if get_setting("system_status") == "OFF":
                bot.send_message(user_id, "⛔ Bot is currently OFF")
                return

            # ❌ FORCE JOIN
            if not is_user_joined(user_id):
                bot.send_message(user_id, force_join_message(user_id))
                return

            # typing
            bot.send_chat_action(user_id, "typing")

            # downloading msg
            msg = bot.send_message(user_id, "⏳ Downloading...")

            try:
                res = download_video(url, platform)

                if res.get("status"):
                    video = res.get("video")

                    # delete downloading
                    try:
                        bot.delete_message(user_id, msg.message_id)
                    except:
                        pass

                    # uploading animation
                    bot.send_chat_action(user_id, "upload_video")

                    bot.send_video(
                        user_id,
                        video,
                        caption=f"Via: @{bot.get_me().username}"
                    )

                    bot.send_message(user_id, "Created: @Create_Our_own_bot")

                    # stats
                    add_download(user_id, platform)

                    # RECEIVER SYSTEM
                    if get_setting("receiver_status") == "ON":
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
                    try:
                        bot.delete_message(user_id, msg.message_id)
                    except:
                        pass

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
        thread = threading.Thread(
            target=run_bot,
            args=(bot, f"UserBot-{token[:6]}")
        )
        thread.daemon = True
        thread.start()

    except Exception as e:
        print("❌ Start error:", e)

# ==============================
# START ALL BOTS
# ==============================
def start_all_bots():
    print("🔥 Loading all user bots...")

    try:
        bots = get_all_bots()

        if not bots:
            print("⚠️ No bots found in database")
            return

        for b in bots:
            token = b.get("token")
            platform = b.get("platform", "TikTok")

            if token:
                start_user_bot(token, platform)

    except Exception as e:
        print("❌ Load error:", e)
