from config import MAIN_BOT_TOKEN
import telebot

# ==============================
# BOT (for checking)
# ==============================
bot = telebot.TeleBot(MAIN_BOT_TOKEN)

# ==============================
# CHANNELS
# ==============================
CHANNELS = [
    "@systemdownloadernews",
    "@systemfor"
]

# ==============================
# CHECK USER JOINED
# ==============================
def is_user_joined(user_id):
    for ch in CHANNELS:
        try:
            member = bot.get_chat_member(ch, user_id)

            print(f"[CHECK] {user_id} in {ch} => {member.status}")

            if member.status not in ["member", "administrator", "creator"]:
                return False

        except Exception as e:
            print(f"[ERROR] {ch} =>", e)
            return False

    return True

# ==============================
# FORCE JOIN MESSAGE
# ==============================
def force_join_message(user_id):
    text = "🔒 Please join channels first:\n\n"

    for ch in CHANNELS:
        text += f"👉 https://t.me/{ch.replace('@','')}\n"

    text += "\n✅ Then press /start"

    return text
