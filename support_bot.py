import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from openai import OpenAI

from database import (
    get_user_bots,
    get_total_downloads,
    save_message,
    get_user_history
)

# ==============================
# ENV
# ==============================
BOT_TOKEN = os.getenv("SUPPORT_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
client = OpenAI(api_key=OPENAI_KEY)

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
        bot.send_message(
            user_id,
            "❌ Go to @Create_Our_own_bot to connect a new Bot and start Bot System."
        )
        return

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for l in LANGS:
        kb.add(KeyboardButton(l))

    bot.send_message(user_id, "🌍 Choose your language:", reply_markup=kb)


# ==============================
# LANGUAGE
# ==============================
@bot.message_handler(func=lambda m: m.text in LANGS)
def set_lang(message):
    user_id = message.chat.id
    user_lang[user_id] = LANGS[message.text]

    bot.send_message(user_id, "✅ Language set\n💬 Ask anything...")


# ==============================
# STATS
# ==============================
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        return

    total = get_total_downloads()
    bot.send_message(message.chat.id, f"📊 Downloads: {total}")


# ==============================
# HISTORY
# ==============================
@bot.message_handler(commands=['history'])
def history(message):
    user_id = message.chat.id

    data = get_user_history(user_id, 10)

    if not data:
        bot.send_message(user_id, "📭 No history")
        return

    text = "🧠 HISTORY:\n\n"

    for h in data:
        role = "👤" if h["role"] == "user" else "🤖"
        text += f"{role}: {h['text']}\n\n"

    bot.send_message(user_id, text)


# ==============================
# AI SUPPORT
# ==============================
@bot.message_handler(func=lambda m: True)
def ai_support(message):
    user_id = message.chat.id
    text = message.text

    if not has_bot(user_id):
        bot.send_message(user_id, "❌ Create bot first:\n@Create_Our_own_bot")
        return

    if user_id not in user_lang:
        bot.send_message(user_id, "⚠️ Choose language first")
        return

    lang = user_lang[user_id]

    try:
        bot.send_chat_action(user_id, "typing")

        # 🔥 GET MEMORY
        history = get_user_history(user_id, 10)

        messages_list = [
            {
                "role": "system",
                "content": f"You are a Telegram bot support expert. Speak {lang}. Fix errors fast."
            }
        ]

        for h in history:
            messages_list.append({
                "role": h["role"],
                "content": h["text"]
            })

        messages_list.append({
            "role": "user",
            "content": text
        })

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages_list
        )

        reply = response.choices[0].message.content

        if not reply:
            bot.send_message(user_id, "❌ No response")
            return

        bot.send_message(user_id, reply)

        # 🔥 SAVE MEMORY
        save_message(user_id, "user", text)
        save_message(user_id, "assistant", reply)

        # 🔥 ADMIN FALLBACK
        if "CONTACT ADMIN" in reply.upper():
            forward_admin(message)

    except Exception as e:
        print("AI ERROR:", e)

        bot.send_message(user_id, "❌ Error → sent to admin")
        forward_admin(message)


# ==============================
# ADMIN
# ==============================
def forward_admin(message):
    try:
        user = message.from_user

        bot.send_message(
            ADMIN_ID,
            f"🚨 ISSUE\n@{user.username}\nID: {user.id}\n\n{message.text}"
        )
    except:
        pass


# ==============================
# RUN
# ==============================
def run():
    print("🤖 SUPPORT AI RUNNING...")
    bot.infinity_polling(skip_pending=True)
