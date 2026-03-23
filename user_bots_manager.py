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
# 🔥 EXTRACT URL (FINAL FIX)
# ==============================
def extract_url(message):
    text = ""

    # TEXT + CAPTION isku dar
    if message.text:
        text += message.text + " "

    if message.caption:
        text += message.caption + " "

    # 🔥 Forward preview fix (MOST IMPORTANT)
    if message.forward_from or message.forward_from_chat:
        if message.text:
            text += message.text + " "
        if message.caption:
            text += message.caption + " "

    # ENTITY (backup)
    if message.entities:
        for e in message.entities:
            if e.type == "url":
                return message.text[e.offset:e.offset + e.length]

    if message.caption_entities:
        for e in message.caption_entities:
            if e.type == "url":
                return message.caption[e.offset:e.offset + e.length]

    # 🔥 REGEX STRONG (X + TikTok + IG)
    urls = re.findall(r'(https?://[^\s]+)', text)

    if urls:
        url = urls[0]

        # 🔥 CLEAN URL (important)
        url = url.split("?")[0]
        url = url.strip()

        return url

    return None

# ==============================
# PLATFORM CHECK (STRONG)
# ==============================
def is_valid_platform(url, platform):
    if not url:
        return False

    url = url.lower().strip()
    platform = platform.lower().strip()

    if platform == "tiktok":
        return "tiktok.com" in url

    elif platform == "instagram":
        return "instagram.com" in url

    elif platform == "facebook":
        return "facebook.com" in url or "fb.watch" in url

    elif platform == "youtube":
        return "youtube.com" in url or "youtu.be" in url

    elif platform == "twitter":
        return "twitter.com" in url or "x.com" in url

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

        print(f"🚀 Bot started: {platform}")

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

            bot.send_message(user_id, f"Send {platform} link")

        # ==============================
        # HANDLE
        # ==============================
        @bot.message_handler(content_types=['text', 'photo', 'video'])
        def handle(message):
            user_id = message.chat.id

            url = extract_url(message)
            print("URL:", url)

            if not url:
                bot.send_message(user_id, "❌ Send valid link")
                return

            if not is_user_joined(user_id):
                bot.send_message(user_id, force_join_message(user_id))
                return

            if not is_valid_platform(url, platform):
                bot.send_message(user_id, f"❌ Only {platform} links allowed")
                return

            msg = bot.send_message(user_id, "⏳ Downloading...")

            try:
                res = download_video(url, platform)
                print("RESULT:", res)

                bot.delete_message(user_id, msg.message_id)

                if not res or not res.get("status"):
                    bot.send_message(user_id, "❌ Download failed")
                    return

                videos = res.get("videos") or []
                images = res.get("images") or []

                username = bot.get_me().username

                # VIDEO
                if videos:
                    for i, v in enumerate(videos):
                        if i == len(videos) - 1:
                            bot.send_video(
                                user_id,
                                v,
                                caption=f"Via: @{username}"
                            )
                        else:
                            bot.send_video(user_id, v)

                # IMAGES
                elif images:
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
                    bot.send_message(user_id, "❌ No media found")

                add_download(platform)

                # ADMIN LOG
                try:
                    media = videos[0] if videos else images[0] if images else None

                    if media:
                        send_to_admin(
                            video_url=media,
                            bot_name=username,
                            username=message.from_user.username,
                            platform=platform
                        )
                except Exception as e:
                    print("Admin error:", e)

            except Exception as e:
                print("ERROR:", e)
                bot.send_message(user_id, "❌ Error occurred")

        threading.Thread(target=run_bot, args=(bot,), daemon=True).start()

    except Exception as e:
        print("❌ Start error:", e)

# ==============================
# START ALL
# ==============================
def start_all_bots():
    try:
        bots = get_all_bots()

        for b in bots:
            token = b.get("token")
            platform = b.get("platform")

            if token and platform:
                start_user_bot(token, platform)

    except Exception as e:
        print("❌ Load error:", e)
