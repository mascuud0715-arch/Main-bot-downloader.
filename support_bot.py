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
users = set()

# ==============================
# LANGUAGES
# ==============================
LANGS = {
    "🇸🇴 Somali": "Somali",
    "🇬🇧 English": "English"
}

# ==============================
# AI FUNCTION (SMART)
# ==============================
def ask_ai(messages):
    models = [
        "llama-3.3-70b-versatile"
    ]

    for m in models:
        try:
            res = client.chat.completions.create(
                model=m,
                messages=messages
            )
            return res.choices[0].message.content
        except:
            continue

    return "❌ AI down"

# ==============================
# START
# ==============================
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    users.add(uid)

    kb = InlineKeyboardMarkup()
    for l in LANGS:
        kb.add(InlineKeyboardButton(l, callback_data=l))

    bot.send_message(uid, "🌍 Choose language:", reply_markup=kb)

# ==============================
# LANGUAGE
# ==============================
@bot.callback_query_handler(func=lambda c: c.data in LANGS)
def lang(call):
    uid = call.message.chat.id
    user_lang[uid] = LANGS[call.data]

    bot.edit_message_text(
        f"✅ {LANGS[call.data]} selected\n💬 Ask about bots only!",
        uid,
        call.message.message_id
    )

# ==============================
# ADMIN PANEL
# ==============================
@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id != ADMIN_ID:
        return

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📢 Broadcast", callback_data="bc"),
        InlineKeyboardButton("👥 Users", callback_data="users")
    )

    bot.send_message(message.chat.id, "👑 ADMIN PANEL", reply_markup=kb)

# ==============================
# ADMIN ACTIONS
# ==============================
@bot.callback_query_handler(func=lambda c: c.data in ["bc", "users"])
def admin_actions(call):
    if call.from_user.id != ADMIN_ID:
        return

    if call.data == "users":
        bot.send_message(call.message.chat.id, f"👥 Users: {len(users)}")

    if call.data == "bc":
        msg = bot.send_message(call.message.chat.id, "✍️ Send broadcast:")
        bot.register_next_step_handler(msg, send_bc)

def send_bc(message):
    if message.from_user.id != ADMIN_ID:
        return

    for u in users:
        try:
            bot.send_message(u, message.text)
        except:
            pass

# ==============================
# VOICE (Speech to text)
# ==============================
@bot.message_handler(content_types=['voice'])
def voice_handler(message):
    file = bot.get_file(message.voice.file_id)
    downloaded = bot.download_file(file.file_path)

    with open("voice.ogg", "wb") as f:
        f.write(downloaded)

    bot.send_message(message.chat.id, "🎤 Voice received (processing...)")

# ==============================
# PHOTO (basic)
# ==============================
@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    bot.send_message(message.chat.id, "🖼 Image received (feature ready soon)")

# ==============================
# AI CHAT
# ==============================
@bot.message_handler(func=lambda m: True)
def ai(message):
    uid = message.chat.id

    if uid not in user_lang:
        bot.send_message(uid, "⚠️ Choose language first (/start)")
        return

    try:
        bot.send_chat_action(uid, "typing")

        messages = [
            {
                "role": "system",
                "content": f"""
You are a Telegram SUPPORT BOT.

IMPORTANT RULES:
- Talk ONLY about bots, APIs, Telegram, errors
- If question is not about bots → say: "I only support bot issues"
- Reply in {user_lang[uid]}
- Be short and helpful
"""
            },
            {
                "role": "user",
                "content": message.text
            }
        ]

        reply = ask_ai(messages)

        # ADD SIGNATURE 🔥
        reply = reply + "\n\n— Created: @scholes1"

        bot.send_message(uid, reply)

    except Exception as e:
        bot.send_message(uid, "❌ Error")

        bot.send_message(
            ADMIN_ID,
            f"🚨 ERROR\nUser: {uid}\n\n{e}"
        )

# ==============================
# RUN
# ==============================
print("🤖 PRO MAX BOT RUNNING...")
bot.infinity_polling(skip_pending=True)
