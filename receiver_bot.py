import telebot
from config import RECEIVER_BOT_TOKEN, ADMIN_ID

bot = telebot.TeleBot(RECEIVER_BOT_TOKEN)

def send_to_admin(video, caption):
    bot.send_video(ADMIN_ID, video, caption=caption)
