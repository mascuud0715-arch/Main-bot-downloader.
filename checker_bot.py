import telebot
from config import CHECKER_BOT_TOKEN
from database import get_channels

bot = telebot.TeleBot(CHECKER_BOT_TOKEN, parse_mode="HTML")

# ==============================
# CHECK USER JOIN
# ==============================
def is_user_joined(user_id):
    channels = get_channels()

    if not channels:
        return True  # no channels = allow

    for ch in channels:
        channel_id = ch.get("channel_id")

        try:
            member = bot.get_chat_member(channel_id, user_id)

            if member.status not in ["member", "administrator", "creator"]:
                return False

        except:
            return False

    return True

# ==============================
# FORCE JOIN MESSAGE
# ==============================
def force_join_message(user_id):
    channels = get_channels()

    text = "⚠️ You must join our channels first:\n\n"

    for ch in channels:
        text += f"👉 {ch.get('channel_id')}\n"

    text += "\nAfter joining, send /start again."

    return text

# ==============================
# TEST COMMAND
# ==============================
@bot.message_handler(commands=['check'])
def check_user(message):
    user_id = message.chat.id

    if is_user_joined(user_id):
        bot.send_message(user_id, "✅ You joined all channels")
    else:
        bot.send_message(user_id, force_join_message(user_id))

# ==============================
# RUN
# ==============================
print("Checker bot running...")
bot.infinity_polling()
