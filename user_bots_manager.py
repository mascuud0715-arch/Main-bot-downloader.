import telebot
import threading
import time
import re

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

running_bots = {}

# ==============================
# CLEAN TOKEN
# ==============================
def clean_token(token):
    return token.replace(" ", "").strip()

# ==============================
# 🔥 EXTRACT URL (FINAL FIX)
# ==============================
def extract_url(message):
    text = ""

    if message.text:
        text = message.text

    elif message.caption:
        text = message.caption

    # 🔥 find ALL urls
    urls = re.findall(r'(https?://[^\s]+)', text)

    if urls:
        return urls[0]

    return None

# ==============================
# PLATFORM CHECK
# ==============================
def is_valid_platform(url, platform):
    if not url:
        return False

    url = url.lower().strip().replace(" ", "")

    if platform == "tiktok":
        return any(x in url for x in [
            "tiktok.com",
            "vt.tiktok.com",
            "vm.tiktok.com"
        ])

    elif platform == "instagram":
        return any(x in url for x in [
            "instagram.com",
            "instagr.am"
        ])

    elif platform == "facebook":
        return any(x in url for x in [
            "facebook.com",
            "fb.watch",
            "fb.com"
        ])

    elif platform == "youtube":
        return any(x in url for x in [
            "youtube.com",
            "youtu.be"
        ])

    elif platform == "twitter":
        return any(x in url for x in [
            "twitter.com",
            "x.com"
        ])

    return False

# ==============================
# BOT THREAD
# ==============================
def run_bot(bot):
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=60)
        except Exception as e:
            print("⚠️ Restarting bot...", e)
            time.sleep(5)

# ==============================
# START BOT
# ==============================
def start_user_bot(token, platform):
    try:
        token = clean_token(token)

        if not token or ":" not in token:
            print("❌ Invalid token:", token)
            return

        if token in running_bots:
            return

        bot = telebot.TeleBot(token, parse_mode="HTML")
        running_bots[token] = bot

        print(f"🚀 Bot started: {token[:10]} ({platform})")

        # START
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
                f"👋 Send {platform.upper()} link only",
                reply_markup=kb
            )

        # CREATE BUTTON
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
        # HANDLE 🔥 FINAL
        # ==============================
        @bot.message_handler(content_types=['text', 'photo', 'video'])
        def handle(message):
            user_id = message.chat.id

            url = extract_url(message)

            print("URL:", url)  # DEBUG

            if not url:
                bot.send_message(user_id, "❌ Send valid link")
                return

            save_user_bot(user_id, token)

            if not is_user_joined(user_id):
                bot.send_message(user_id, force_join_message(user_id))
                return

            if not is_valid_platform(url, platform):
                bot.send_message(
                    user_id,
                    f"❌ This bot supports only {platform.upper()} links!"
                )
                return

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

                    username = bot.get_me().username

                    # ===== VIDEO =====
                    if videos:
                        for i, v in enumerate(videos):
                            if i == len(videos) - 1:
                                bot.send_video(
                                    user_id,
                                    v,
                                    caption=f"Via: @{username}\nCreated: @Create_Our_own_bot"
                                )
                            else:
                                bot.send_video(user_id, v)

                    # ===== IMAGE =====
                    elif images:
                        for i, img in enumerate(images):
                            if i == len(images) - 1:
                                bot.send_photo(
                                    user_id,
                                    img,
                                    caption=f"Via: @{username}\nCreated: @Create_Our_own_bot"
                                )
                            else:
                                bot.send_photo(user_id, img)

                    else:
                        bot.send_message(user_id, "❌ No media found")

                    add_download(platform)

                    try:
                        send_to_admin(
                            video_url=videos[0] if videos else images[0],
                            bot_name=username,
                            username=message.from_user.username,
                            platform=platform
                        )
                    except Exception as e:
                        print("Admin error:", e)

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

        thread = threading.Thread(target=run_bot, args=(bot,), daemon=True)
        thread.start()

    except Exception as e:
        print("❌ Start error:", e)

# ==============================
# START ALL
# ==============================
def start_all_bots():
    try:
        bots = get_all_bots()

        print(f"🤖 Loading {len(bots)} bots...")

        for b in bots:
            token = b.get("token")
            platform = b.get("platform")

            if token and platform:
                start_user_bot(token, platform)

    except Exception as e:
        print("❌ Load error:", e)
