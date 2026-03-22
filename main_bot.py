import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import MAIN_BOT_TOKEN
from database import bots

bot = telebot.TeleBot(MAIN_BOT_TOKEN)

user_step = {}

@bot.message_handler(commands=['start'])
def start(msg):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ ADD BOT", "🤖 BOTS", "❌ REMOVE BOT")
    bot.send_message(msg.chat.id, "Ku soo dhawoow Bot Builder", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == "➕ ADD BOT")
def add_bot(msg):
    bot.send_message(msg.chat.id, "Geli BOT TOKEN:")
    user_step[msg.chat.id] = "token"

@bot.message_handler(func=lambda m: True)
def handle(msg):
    step = user_step.get(msg.chat.id)

    if step == "token":
        token = msg.text
        
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("TikTok", "Instagram", "X")

        user_step[msg.chat.id] = {"token": token}
        bot.send_message(msg.chat.id, "Dooro platform:", reply_markup=kb)

    elif isinstance(step, dict):
        bots.insert_one({
            "user_id": msg.chat.id,
            "token": step["token"],
            "platform": msg.text
        })

        bot.send_message(msg.chat.id, "Bot waa la daray ✅")
        user_step[msg.chat.id] = None

bot.infinity_polling()
