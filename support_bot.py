import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from openai import OpenAI

# ==============================
# ENV
# ==============================
BOT_TOKEN = os.getenv("SUPPORT_BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

client = OpenAI(
    api_key=GROQ_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# ==============================
# MEMORY
# ==============================
user_lang = {}

# ==============================
# LANGUAGES
# ==============================
LANGS = {
    "🇸🇴 Somali": "Somali",
    "🇬🇧 English": "English",
    "🇸🇦 Arabic": "Arabic",
    "🇪🇸 Spanish": "Spanish",
    "🇫🇷 French": "French",
    "🇩🇪 German": "German",
    "🇮🇹 Italian": "Italian",
    "🇹🇷 Turkish": "Turkish",
    "🇮🇳 Hindi": "Hindi",
    "🇨🇳 Chinese": "Chinese"
}

# ==============================
# AI FUNCTION (AUTO MODEL 🔥)
# ==============================
def ask_ai(messages):
    models = [
        "llama-3.1-8b-instant",
        "gemma-7b-it",
        "llama3-8b-8192"
    ]

    for m in models:
        try:
            res = client.chat.completions.create(
                model=m,
                messages=messages
            )
            return res.choices[0].message.content
        except Exception as e:
            print(f"{m} failed:", e)
            continue

    return "❌ AI temporarily down, try again later."

# ==============================
# START
# ==============================
@bot.message_handler(commands=['start'])
def start(message):
    kb = InlineKeyboardMarkup(row_width=2)
    for l in LANGS:
        kb.add(InlineKeyboardButton(l, callback_data=l))

    bot.send_message(
        message.chat.id,
        "🌍 <b>WELCOME TO AI SUPPORT BOT</b>\n\n"
        "🤖 I can help you fix:\n"
        "• Download problems\n"
        "• Bot errors\n"
        "• API issues\n\n"
        "👇 Choose your language:",
        reply_markup=kb
    )

# ==============================
# LANGUAGE SELECT
# ==============================
@bot.callback_query_handler(func=lambda c: c.data in LANGS)
def set_lang(call):
    user_id = call.message.chat.id
    user_lang[user_id] = LANGS[call.data]

    bot.edit_message_text(
        f"✅ <b>{LANGS[call.data]} selected</b>\n\n💬 Ask anything...",
        user_id,
        call.message.message_id
    )

# ==============================
# AI CHAT
# ==============================
@bot.message_handler(func=lambda m: True)
def ai(message):
    user_id = message.chat.id

    if user_id not in user_lang:
        bot.send_message(user_id, "⚠️ Please choose language first (/start)")
        return

    try:
        bot.send_chat_action(user_id, "typing")

        messages = [
            {
                "role": "system",
                "content": f"""
You are a professional Telegram support bot.

Language: {user_lang[user_id]}

You help users fix:
- Download errors
- Token issues
- Railway problems
- Bot errors

Rules:
- Speak ONLY {user_lang[user_id]}
- Be short and clear
- Give solutions
- If not solvable → say CONTACT ADMIN
"""
            },
            {
                "role": "user",
                "content": message.text
            }
        ]

        reply = ask_ai(messages)

        bot.send_message(user_id, reply)

        # haddii AI u baahato admin
        if "CONTACT ADMIN" in reply.upper():
            bot.send_message(
                ADMIN_ID,
                f"🚨 USER NEED HELP\n\nID: {user_id}\nMSG: {message.text}"
            )

    except Exception as e:
        print("ERROR:", e)

        bot.send_message(user_id, "❌ System error, admin notified")

        bot.send_message(
            ADMIN_ID,
            f"🚨 ERROR\nUser: {user_id}\n\n{e}"
        )

# ==============================
# RUN
# ==============================
print("🤖 AI SUPPORT BOT RUNNING...")
bot.infinity_polling(skip_pending=True)
