import telebot
from config import CHECKER_BOT_TOKEN
from database import get_channels

bot = telebot.TeleBot(CHECKER_BOT_TOKEN, parse_mode="HTML")

# ==============================
# CHECK USER JOINED
# ==============================
def is_user_joined(user_id):
    channels = get_channels()

    if not channels:
        return True  # haddii channel la'aan, allow

    for ch in channels:
        try:
            member = bot.get_chat_member(ch, user_id)

            if member.status not in ["member", "administrator", "creator"]:
                return False

        except Exception as e:
            print("Checker error:", e)
            return False

    return True

# ==============================
# FORCE JOIN MESSAGE
# ==============================
def force_join_message(user_id):
    channels = get_channels()

    if not channels:
        return "⚠️ No channels configured"

    text = "🚫 Please join all channels first:\n\n"

    for ch in channels:
        text += f"👉 {ch}\n"

    text += "\n✅ Then send /start again"

    return text

# ==============================
# TEST COMMAND (ADMIN USE)
# ==============================
@bot.message_handler(commands=['check'])
def check(message):
    user_id = message.chat.id

    if is_user_joined(user_id):
        bot.send_message(user_id, "✅ You joined all channels")
    else:
        bot.send_message(user_id, force_join_message(user_id))
