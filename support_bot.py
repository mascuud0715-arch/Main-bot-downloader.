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
# START
# ==============================
@bot.message_handler(commands=['start'])
def start(message):
    kb = InlineKeyboardMarkup(row_width=2)
    for l in LANGS:
        kb.add(InlineKeyboardButton(l, callback_data=l))

    bot.send_message(
        message.chat.id,
        "🌍 <b>Welcome to FREE AI Support Bot</b>\n\n👇 Choose language:",
        reply_markup=kb
    )

# ==============================
# LANGUAGE
# ==============================
@bot.callback_query_handler(func=lambda c: c.data in LANGS)
def lang(call):
    user_id = call.message.chat.id
    user_lang[user_id] = LANGS[call.data]

    bot.edit_message_text(
        f"✅ {LANGS[call.data]} selected\n💬 Ask anything!",
        user_id,
        call.message.message_id
    )

# ==============================
# AI
# ==============================
@bot.message_handler(func=lambda m: True)
def ai(message):
    user_id = message.chat.id

    if user_id not in user_lang:
        bot.send_message(user_id, "⚠️ Choose language first (/start)")
        return

    try:
        bot.send_chat_action(user_id, "typing")

        res = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {
                    "role": "system",
                    "content": f"Reply in {user_lang[user_id]}. Help user like support bot."
                },
                {
                    "role": "user",
                    "content": message.text
                }
            ]
        )

        reply = res.choices[0].message.content

        bot.send_message(user_id, reply)

    except Exception as e:
        print("GROQ ERROR:", e)

        bot.send_message(user_id, f"❌ Error:\n{e}")

        bot.send_message(
            ADMIN_ID,
            f"🚨 ERROR\n\nUser: {user_id}\n\n{e}"
        )

# ==============================
# RUN
# ==============================
print("🤖 GROQ BOT RUNNING...")
bot.infinity_polling(skip_pending=True)
