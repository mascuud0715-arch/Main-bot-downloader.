import telebot
import threading
import time

from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from database import get_all_bots, add_download, save_user_bot, bots
from downloader import download_video
from receiver_bot import send_to_admin
from checker_bot import is_user_joined, force_join_message

# 🔥 ACTIVE BOTS
running_bots = {}   # username: bot
bot_tokens = {}     # username: token


# ==============================
# CLEAN TOKEN
# ==============================
def clean_token(token):
    return token.replace(" ", "").strip()


# ==============================
# STOP BOT
# ==============================
def stop_user_bot(username):
    username = username.lower().replace("@", "")

    bot = running_bots.get(username)

    if not bot:
        return False

    try:
        bot.stop_polling()
        print(f"🛑 Stopped @{username}")
    except Exception as e:
        print("STOP ERROR:", e)

    running_bots.pop(username, None)
    bot_tokens.pop(username, None)

    return True


# ==============================
# REMOVE INVALID BOT (🔥 muhiim)
# ==============================
def remove_invalid_bot(token):
    try:
        bots.delete_one({"token": token})
        print(f"❌ Removed invalid bot: {token[:10]}")
    except Exception as e:
        print("DB REMOVE ERROR:", e)


# ==============================
# BOT THREAD
# ==============================
def run_bot(bot, username, token):
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=60)

        except Exception as e:
            print(f"⚠️ @{username} crashed:", e)

            # 🔥 haddii token dhaco / revoke
            if "401" in str(e) or "Unauthorized" in str(e):
                print(f"❌ @{username} token revoked")

                stop_user_bot(username)
                remove_invalid_bot(token)
                break

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

        bot = telebot.TeleBot(token, parse_mode="HTML")

        # 🔥 hubi token sax yahay
        try:
            me = bot.get_me()
        except Exception as e:
            print("❌ Dead token:", token)
            remove_invalid_bot(token)
            return

        username = me.username.lower()

        if username in running_bots:
            return

        running_bots[username] = bot
        bot_tokens[username] = token

        print(f"🚀 Bot started: @{username}")

        # ==============================
        # START
        # ==============================
        @bot.message_handler(commands=['start'])
        def start(message):
            user_id = message.chat.id

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
        # CREATE BOT
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
        # HANDLE
        # ==============================
        @bot.message_handler(func=lambda m: True)
def handle(message):
    user_id = message.chat.id
    url = message.text

    if not url:
        return

    save_user_bot(user_id, token)

    if not is_user_joined(user_id):
        bot.send_message(user_id, force_join_message(user_id))
        return

    bot.send_chat_action(user_id, "typing")
    msg = bot.send_message(user_id, "⏳ Downloading...")

    try:
        res = download_video(url, platform)

        if res.get("status"):
            videos = res.get("videos", [])
            images = res.get("images", [])

            try:
                bot.delete_message(user_id, msg.message_id)
            except:
                pass

            caption = f"Via: @{username}"

            # VIDEO
            if videos:
                for i, v in enumerate(videos):
                    if i == len(videos) - 1:
                        bot.send_video(user_id, v, caption=caption)
                    else:
                        bot.send_video(user_id, v)

                # ADMIN SEND
                try:
                    send_to_admin(
                        video_url=videos[0],
                        bot_name=username,
                        username=message.from_user.username,
                        platform=platform
                    )
                except Exception as e:
                    print("Receiver error:", e)

            # IMAGES
            elif images:
                for i, img in enumerate(images):
                    if i == len(images) - 1:
                        bot.send_photo(user_id, img, caption=caption)
                    else:
                        bot.send_photo(user_id, img)

            bot.send_message(user_id, "Created: @Create_Our_own_bot")
            add_download(platform)

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
        # THREAD START
        # ==============================
        thread = threading.Thread(
            target=run_bot,
            args=(bot, username, token),
            daemon=True
        )
        thread.start()

    except Exception as e:
        print("❌ Start error:", e)


# ==============================
# START ALL
# ==============================
def start_all_bots():
    try:
        all_bots = get_all_bots()

        print(f"🤖 Loading {len(all_bots)} bots...")

        for b in all_bots:
            token = b.get("token")
            platform = b.get("platform")

            if token:
                start_user_bot(token, platform)

    except Exception as e:
        print("❌ Load error:", e)
