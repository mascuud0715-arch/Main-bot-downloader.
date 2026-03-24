import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from openai import OpenAI

from database import get_user_bots

# ==============================
# ENV
# ==============================
BOT_TOKEN = os.getenv("SUPPORT_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise Exception("❌ SUPPORT_BOT_TOKEN missing")

if not OPENAI_KEY:
    raise Exception("❌ OPENAI_API_KEY missing")

client = OpenAI(api_key=OPENAI_KEY)
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


# ==============================
# CHECK USER
# ==============================
def has_bot(user_id):
    return len(get_user_bots(user_id)) > 0


# ==============================
# START
# ==============================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id

    if not has_bot(user_id):
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton(
                "🤖 Create Bot",
                url="https://t.me/Create_Our_own_bot"
            )
        )

        bot.send_message(
            user_id,
            "❌ Go to @Create_Our_own_bot to connect a new Bot and start Bot System.",
            reply_markup=kb
        )
        return

    bot.send_message(
        user_id,
        "🤖 AI Support is ready\nAsk anything about your bot system 💬"
    )


# ==============================
# AI RESPONSE
# ==============================
@bot.message_handler(func=lambda m: True)
def ai_support(message):
    user_id = message.chat.id
    text = message.text

    if not has_bot(user_id):
        bot.send_message(
            user_id,
            "❌ You must create a bot first:\n@Create_Our_own_bot"
        )
        return

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
You are a Telegram bot support expert.

You help users fix:
- Download errors
- Broadcast issues
- Token errors
- Railway deployment issues
- MongoDB issues

Always:
- Give clear solutions
- Be short and direct
- If not sure → say "contact admin"
"""
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        reply = response.choices[0].message.content

        bot.send_message(user_id, reply)

        # haddii AI ku kalsooni yar (keyword)
        if "contact admin" in reply.lower():
            forward_to_admin(message)

    except Exception as e:
        print("AI ERROR:", e)
        forward_to_admin(message)


# ==============================
# ADMIN FORWARD
# ==============================
def forward_to_admin(message):
    try:
        user = message.from_user

        bot.send_message(
            ADMIN_ID,
            f"""
🚨 AI FAILED - SUPPORT

👤 @{user.username}
🆔 {user.id}

💬 {message.text}
"""
        )

        bot.send_message(message.chat.id, "📩 Sent to admin")

    except:
        bot.send_message(message.chat.id, "❌ Failed")


# ==============================
# RUN
# ==============================
def run():
    print("🤖 AI Support bot running...")
    bot.infinity_polling(skip_pending=True)
