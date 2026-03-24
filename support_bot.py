import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
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

if not OPENAI_KEY:
    raise Exception("❌ OPENAI_API_KEY missing")

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

    kb = InlineKeyboardMarkup(row_width=2)
    for name in LANGS:
        kb.add(InlineKeyboardButton(name, callback_data=name))

    bot.send_message(
        user_id,
        """🌍 <b>Welcome to AI Support Bot</b>

🤖 Waxaan kaa caawinayaa:
• Download problems
• Bot errors
• Token issues
• System bugs

👇 Dooro luuqadaada:""",
        reply_markup=kb
    )


# ==============================
# LANGUAGE SELECT
# ==============================
@bot.callback_query_handler(func=lambda call: call.data in LANGS)
def set_lang(call):
    user_id = call.message.chat.id
    lang = LANGS[call.data]
    user_lang[user_id] = lang

    if lang == "Somali":
        text = "✅ Luqada waa la dejiyay 🇸🇴\n💬 Wax i waydii!"
    elif lang == "English":
        text = "✅ Language set 🇬🇧\n💬 Ask anything!"
    else:
        text = f"✅ Language set: {lang}\n💬 Ask anything!"

    bot.edit_message_text(text, user_id, call.message.message_id)


# ==============================
# STATS
# ==============================
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        return

    total = get_total_downloads()
    bot.send_message(message.chat.id, f"📊 Total Downloads:\n{total}")


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

    txt = "🧠 History:\n\n"
    for h in data:
        role = "👤" if h["role"] == "user" else "🤖"
        txt += f"{role}: {h['text']}\n\n"

    bot.send_message(user_id, txt)


# ==============================
# TEXT
# ==============================
@bot.message_handler(content_types=['text'])
def text_handler(message):
    handle_ai(message, message.text)


# ==============================
# VOICE
# ==============================
@bot.message_handler(content_types=['voice'])
def voice_handler(message):
    handle_ai(message, "User sent a voice message")


# ==============================
# PHOTO
# ==============================
@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    handle_ai(message, "User sent a photo")


# ==============================
# AI CORE
# ==============================
def handle_ai(message, text):
    user_id = message.chat.id

    if not has_bot(user_id):
        bot.send_message(user_id, "❌ Create bot first:\n@Create_Our_own_bot")
        return

    if user_id not in user_lang:
        bot.send_message(user_id, "⚠️ Choose language first (/start)")
        return

    lang = user_lang[user_id]

    try:
        bot.send_chat_action(user_id, "typing")

        history = get_user_history(user_id, 10)

        msgs = [
            {
                "role": "system",
                "content": f"You are a Telegram support bot. Speak {lang}. Help fix problems clearly."
            }
        ]

        for h in history:
            msgs.append({
                "role": h["role"],
                "content": h["text"]
            })

        msgs.append({"role": "user", "content": text})

        # 🔥 WORKING MODEL
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=msgs
        )

        reply = response.choices[0].message.content

        if not reply:
            bot.send_message(user_id, "❌ AI failed")
            return

        bot.send_message(user_id, reply)

        # SAVE MEMORY
        save_message(user_id, "user", text)
        save_message(user_id, "assistant", reply)

    except Exception as e:
        print("AI ERROR:", e)

        bot.send_message(
            user_id,
            f"❌ AI Error:\n{e}"
        )

        forward_admin(message)


# ==============================
# ADMIN
# ==============================
def forward_admin(message):
    try:
        user = message.from_user

        bot.send_message(
            ADMIN_ID,
            f"""🚨 ISSUE

👤 @{user.username}
🆔 {user.id}

💬 {message.text}"""
        )
    except:
        pass


# ==============================
# RUN
# ==============================
def run():
    print("🤖 SUPPORT BOT RUNNING...")
    bot.infinity_polling(skip_pending=True)
