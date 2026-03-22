import telebot
from config import CHECKER_BOT_TOKEN

bot = telebot.TeleBot(CHECKER_BOT_TOKEN)

def is_joined(user_id, channel):
    try:
        member = bot.get_chat_member(channel, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False
