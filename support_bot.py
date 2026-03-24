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
        "🌍 <b>WELCOME TO SUPPORT BOT</b>\n\n"
        "🤖 Waxaan kaa caawin karaa:\n"
        "• Sida bot loo sameeyo\n"
        "• Errors (token / hosting)\n"
        "• Downloader bots\n\n"
        "👇 Dooro luqad:",
        reply_markup=kb
    )

# ==============================
# LANGUAGE
# ==============================
@bot.callback_query_handler(func=lambda c: c.data in LANGS)
def set_lang(call):
    uid = call.message.chat.id
    user_lang[uid] = LANGS[call.data]

    bot.edit_message_text(
        f"✅ {LANGS[call.data]} selected\n💬 Ask about bots only!",
        uid,
        call.message.message_id
    )

# ==============================
# ADMIN PANEL BUTTON
# ==============================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"),
        InlineKeyboardButton("👥 Users", callback_data="users"),
        InlineKeyboardButton("📊 Stats", callback_data="stats"),
        InlineKeyboardButton("❌ Close", callback_data="close")
    )

    bot.send_message(message.chat.id, "👑 <b>ADMIN PANEL</b>", reply_markup=kb)

# ==============================
# ADMIN BUTTON ACTIONS
# ==============================
@bot.callback_query_handler(func=lambda c: c.data in ["broadcast","users","stats","close"])
def admin_actions(call):
    if call.from_user.id != ADMIN_ID:
        return

    if call.data == "users":
        bot.send_message(call.message.chat.id, f"👥 Total Users: {len(users)}")

    elif call.data == "stats":
        bot.send_message(call.message.chat.id, "📊 Bot running нормально ✅")

    elif call.data == "broadcast":
        msg = bot.send_message(call.message.chat.id, "✍️ Send message to broadcast:")
        bot.register_next_step_handler(msg, send_broadcast)

    elif call.data == "close":
        bot.delete_message(call.message.chat.id, call.message.message_id)

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
    bot.send_message(message.chat.id, "🎤 Voice received (processing soon)")

# ==============================
# PHOTO
# ==============================
@bot.message_handler(content_types=['photo'])
def photo(message):
    bot.send_message(message.chat.id, "🖼 Image received (AI feature coming)")

# ==============================
# AI CHAT
# ==============================
@bot.message_handler(func=lambda m: True)
def ai(message):
    uid = message.chat.id

    if uid not in user_lang:
        bot.send_message(uid, "⚠️ Dooro luqad marka hore (/start)")
        return

    try:
        bot.send_chat_action(uid, "typing")

        messages = [
            {
                "role": "system",
                "content": f"""
You are a Telegram BOT SUPPORT EXPERT.

STRICT RULES:
- ONLY talk about bots, Telegram, APIs, errors
- Always guide user to @Create_Our_own_bot to create bots
- Explain:
  • How to create bot using BotFather
  • How to get TOKEN
  • How to deploy (Railway)
- If not bot-related → say: "I only support bot issues"

Language: {user_lang[uid]}
Keep answers short and clear.
"""
            },
            {
                "role": "user",
                "content": message.text
            }
        ]

        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )

        reply = res.choices[0].message.content

        # SIGNATURE
        reply += "\n\n— Created: scholes1"

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
print("🤖 SUPPORT BOT PRO RUNNING...")
bot.infinity_polling(skip_pending=True)
