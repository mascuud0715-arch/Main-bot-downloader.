import telebot
from telebot.types import ReplyKeyboardMarkup
from config import ADMIN_BOT_TOKEN, ADMIN_ID

bot = telebot.TeleBot(ADMIN_BOT_TOKEN)

@bot.message_handler(commands=['start'])
def admin_panel(msg):
    if msg.chat.id != ADMIN_ID:
        return
    
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📢 Broadcast", "📊 Stats", "🎥 Media Stats")
    kb.add("➕ Add Channel", "📋 Channels")
    kb.add("🔄 Receiver On", "🔄 Receiver Off")

    bot.send_message(msg.chat.id, "Admin Panel", reply_markup=kb)

bot.infinity_polling()
