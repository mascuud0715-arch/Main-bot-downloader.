import telebot
import threading
import time
import re
import requests

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
# 🔥 EXPAND SHORT URL (TikTok fix)
# ==============================
def expand_url(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=10)
        return r.url
    except:
        return url

# ==============================
# 🔥 EXTRACT URL (ULTRA FIX FINAL)
# ==============================
def extract_url(message):
    text = ""

    if message.text:
        text += message.text + " "

    if message.caption:
        text += message.caption + " "

    # ENTITY (forward fix)
    if message.entities:
        for e in message.entities:
            if e.type == "url":
                return message.text[e.offset:e.offset + e.length]

    if message.caption_entities:
        for e in message.caption_entities:
            if e.type == "url":
                return message.caption[e.offset:e.offset + e.length]

    # REGEX
    urls = re.findall(r'(https?://[^\s]+)', text)

    if urls:
        url = urls[0]
        url = expand_url(url)  # 🔥 muhiim
        return url

    return None

# ==============================
# PLATFORM CHECK
# ==============================
def is_valid_platform(url, platform):
    if not url:
        return False

    url = url.lower().strip()
    platform = platform.lower().strip()

    if platform == "tiktok":
        return any(x in url for x in [
            "tiktok.com",
            "vt.tiktok.com",
            "vm.tiktok.com"
        ])

    elif platform == "instagram":
        return "instagram.com" in url

    elif platform == "facebook":
        return any(x in url for x in ["facebook.com", "fb.watch"])

    elif platform == "youtube":
        return any(x in url for x in ["youtube.com", "youtu.be"])

    elif platform == "twitter":
        return any(x in url for x in ["twitter.com", "x.com"])

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
        platform = platform.lower().strip()

        if not token or ":" not in token:
            print("❌ Invalid token:", token)
            return

        if token in running_bots:
            return

        bot = telebot.TeleBot(token, parse_mode="HTML")
        running_bots[token] = bot

        print(f"🚀 Bot started: {token[:10]} ({platform})")

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
                f"👋 Send {platform.upper()} link only",
                reply_markup=kb
            )

        # ==============================
        # CREATE BUTTON
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
        @bot.message_handler(content_types=['text', 'photo', 'video'])
        def handle(message):
            user_id = message.chat.id

            url = extract_url(message)
            print("🔥 URL:", url)

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
                print("🔥 RESULT:", res)

                bot.delete_message(user_id, msg.message_id)

                if not res or not res.get("status"):
                    bot.send_message(user_id, "❌ Download failed")
                    return

                videos = res.get("videos") or []
                images = res.get("images") or []

                username = bot.get_me().username

                # ================= VIDEO =================
                if len(videos) > 0:
                    for i, v in enumerate(videos):
                        if i == len(videos) - 1:
                            bot.send_video(
                                user_id,
                                v,
                                caption=f"Via: @{username}"
                            )
                        else:
                            bot.send_video(user_id, v)

                # ================= IMAGES =================
                elif len(images) > 0:
                    for i, img in enumerate(images):
                        if i == len(images) - 1:
                            bot.send_photo(
                                user_id,
                                img,
                                caption=f"Via: @{username}"
                            )
                        else:
                            bot.send_photo(user_id, img)

                else:
                    bot.send_message(user_id, "❌ No media found (Downloader issue)")

                add_download(platform)

                # ADMIN LOG
                try:
                    media_url = None
                    if videos:
                        media_url = videos[0]
                    elif images:
                        media_url = images[0]

                    if media_url:
                        send_to_admin(
                            video_url=media_url,
                            bot_name=username,
                            username=message.from_user.username,
                            platform=platform
                        )
                except Exception as e:
                    print("Admin error:", e)

            except Exception as e:
                print("ERROR:", e)
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
