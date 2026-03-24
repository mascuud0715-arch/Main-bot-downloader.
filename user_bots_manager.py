import telebot
import threading
import time

from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from database import get_all_bots, add_download, save_user_bot, bots, get_owner_by_token
from downloader import download_video
from receiver_bot import send_to_admin
from checker_bot import is_user_joined, force_join_message


running_bots = {}
bot_tokens = {}


def clean_token(token):
    return token.replace(" ", "").strip()


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


def remove_invalid_bot(token):
    try:
        bots.delete_one({"token": token})
        print(f"❌ Removed invalid bot")
    except Exception as e:
        print("DB REMOVE ERROR:", e)


def run_bot(bot, username, token):
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=60)

        except Exception as e:
            print(f"⚠️ @{username} crashed:", e)

            if "401" in str(e) or "Unauthorized" in str(e):
                stop_user_bot(username)
                remove_invalid_bot(token)
                break

            time.sleep(5)


# ==============================
# MENU
# ==============================
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("/help"),
        KeyboardButton("/support")
    )
    kb.add(
        KeyboardButton("/broadcast"),
        KeyboardButton("🤖 Create your bot")
    )
    return kb


def start_user_bot(token, platform):
    try:
        token = clean_token(token)

        if not token or ":" not in token:
            return

        bot = telebot.TeleBot(token, parse_mode="HTML")

        try:
            me = bot.get_me()
        except:
            remove_invalid_bot(token)
            return

        username = me.username.lower()

        if username in running_bots:
            return

        running_bots[username] = bot
        bot_tokens[username] = token

        print(f"🚀 Bot started: @{username}")

        owner_id = get_owner_by_token(token)

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

            bot.send_message(
                user_id,
                f"👋 Send {platform} link to download",
                reply_markup=main_menu()
            )

        # ==============================
        # HELP
        # ==============================
        @bot.message_handler(commands=['help'])
        def help_cmd(message):
            bot.send_message(
                message.chat.id,
                "/Help, Team ? Wait NexT Update"
            )

        # ==============================
        # SUPPORT
        # ==============================
        @bot.message_handler(commands=['support'])
        def support_cmd(message):
            bot.send_message(
                message.chat.id,
                "🛠 Support: @supp_team1_bot"
            )

        # ==============================
        # BROADCAST (OWNER ONLY)
        # ==============================
        @bot.message_handler(commands=['broadcast'])
        def broadcast_cmd(message):
            if message.from_user.id != owner_id:
                bot.send_message(message.chat.id, "❌ Owner only")
                return

            msg = bot.send_message(message.chat.id, "✍️ Send message:")
            bot.register_next_step_handler(msg, send_broadcast)

        def send_broadcast(message):
            text = message.text

            users = []  # 👉 DB kasoo qaado users

            for u in users:
                try:
                    bot.send_message(u, text)
                except:
                    pass

            bot.send_message(message.chat.id, "✅ Sent")

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
        # HANDLE (FIXED)
        # ==============================
        @bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
        def handle(message):
            user_id = message.chat.id
            url = message.text

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

                    if videos:
                        for i, v in enumerate(videos):
                            if i == len(videos) - 1:
                                bot.send_video(user_id, v, caption=caption)
                            else:
                                bot.send_video(user_id, v)

                        send_to_admin(
                            video_url=videos[0],
                            bot_name=username,
                            username=message.from_user.username,
                            platform=platform
                        )

                    elif images:
                        for i, img in enumerate(images):
                            if i == len(images) - 1:
                                bot.send_photo(user_id, img, caption=caption)
                            else:
                                bot.send_photo(user_id, img)

                    bot.send_message(user_id, "Created: @Create_Our_own_bot")
                    add_download(platform)

                else:
                    bot.send_message(user_id, "❌ Download failed")

            except Exception as e:
                print("ERROR:", e)
                bot.send_message(user_id, "❌ Error occurred")

        thread = threading.Thread(
            target=run_bot,
            args=(bot, username, token),
            daemon=True
        )
        thread.start()

    except Exception as e:
        print("❌ Start error:", e)


def start_all_bots():
    try:
        all_bots = get_all_bots()

        for b in all_bots:
            token = b.get("token")
            platform = b.get("platform")

            if token:
                start_user_bot(token, platform)

    except Exception as e:
        print("❌ Load error:", e)
