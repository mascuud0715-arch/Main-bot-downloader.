import os
import telebot
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
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
users = set()

# ==============================
# LANGUAGES
# ==============================
LANGS = {
    "🇸🇴 Somali": "Somali",
    "🇬🇧 English": "English"
}

# ==============================
# DETECT BOT CREATION
# ==============================
def is_bot_creation(text):
    keys = ["create bot", "samee bot", "bot create", "botfather", "token"]
    return any(k in text.lower() for k in keys)

# ==============================
# START
# ==============================
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    users.add(uid)

    kb = InlineKeyboardMarkup(row_width=2)
    for l in LANGS:
        kb.add(InlineKeyboardButton(l, callback_data=l))

    bot.send_message(
        uid,
        "🌟 <b>WELCOME TO PROFESSIONAL AI SUPPORT BOT</b>\n\n"
        "🤖 Waxaan kaa caawinayaa:\n"
        "• Bot creation\n• Errors\n• API issues\n• Telegram problems\n\n"
        "🤖 I help you with:\n"
        "• Creating bots\n• Fixing errors\n• API & hosting\n\n"
        "👇 Choose your language:",
        reply_markup=kb
    )

# ==============================
# LANGUAGE
# ==============================
@bot.callback_query_handler(func=lambda c: c.data in LANGS)
def set_lang(call):
    uid = call.message.chat.id
    user_lang[uid] = LANGS[call.data]

    # Admin keyboard
    if uid == ADMIN_ID:
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(
            KeyboardButton("📢 Broadcast"),
            KeyboardButton("👥 Users"),
            KeyboardButton("📊 Stats")
        )
        bot.send_message(uid, "👑 ADMIN MODE ACTIVE", reply_markup=kb)

    bot.edit_message_text(
        f"✅ {LANGS[call.data]} selected\n\n💬 Ask anything about Telegram bots.",
        uid,
        call.message.message_id
    )

# ==============================
# ADMIN PANEL (KEYBOARD)
# ==============================
@bot.message_handler(func=lambda m: m.text in ["📢 Broadcast","👥 Users","📊 Stats"])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return

    if message.text == "👥 Users":
        bot.send_message(message.chat.id, f"👥 Total users: {len(users)}")

    elif message.text == "📊 Stats":
        bot.send_message(message.chat.id, "📊 Bot running perfectly ✅")

    elif message.text == "📢 Broadcast":
        msg = bot.send_message(message.chat.id, "✍️ Send broadcast message:")
        bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return

    for u in users:
        try:
            bot.send_message(u, f"📢 {message.text}")
        except:
            pass

# ==============================
# VOICE
# ==============================
@bot.message_handler(content_types=['voice'])
def voice(message):
    bot.send_message(
        message.chat.id,
        "🎤 Voice received\n⏳ Processing soon..."
    )

# ==============================
# PHOTO
# ==============================
@bot.message_handler(content_types=['photo'])
def photo(message):
    bot.send_message(
        message.chat.id,
        "🖼 Image received\n🤖 AI analysis coming soon..."
    )

# ==============================
# AI SUPPORT
# ==============================
@bot.message_handler(func=lambda m: True)
def ai(message):
    uid = message.chat.id

    if uid not in user_lang:
        bot.send_message(uid, "⚠️ Please choose language first (/start)")
        return

    try:
        bot.send_chat_action(uid, "typing")

        extra = ""
        if is_bot_creation(message.text):
            extra = "\nAlso you can create bots using @Create_Our_own_bot"

        messages = [
            {
                "role": "system",
                "content": f"""
You are a PROFESSIONAL Telegram Support AI.

RULES:
- Answer ONLY about Telegram, bots, APIs, errors
- If not related → say: "I only support Telegram bot issues"
- Be professional and helpful
- Explain system clearly if asked

Language: {user_lang[uid]}
"""
            },
            {
                "role": "user",
                "content": message.text + extra
            }
        ]

        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )

        reply = res.choices[0].message.content

        reply += "\n\n— SUPPORT TEAM"

        bot.send_message(uid, reply)

    except Exception as e:
        bot.send_message(uid, "❌ System error")

        bot.send_message(
            ADMIN_ID,
            f"🚨 ERROR\nUser: {uid}\n\n{e}"
        )

# ==============================
# RUN
# ==============================
print("🤖 PROFESSIONAL SUPPORT BOT RUNNING...")
