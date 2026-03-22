import threading
import time

# import bots
from main_bot import bot as main_bot
from admin_bot import bot as admin_bot
from receiver_bot import bot as receiver_bot
from checker_bot import bot as checker_bot

# import user bots manager
from user_bots_manager import start_all_bots

# ==============================
# RUN FUNCTION
# ==============================
def run_bot(bot_instance, name):
    print(f"🚀 {name} started")
    while True:
        try:
            bot_instance.infinity_polling(timeout=30, long_polling_timeout=10)
        except Exception as e:
            print(f"❌ {name} crashed: {e}")
            time.sleep(5)

# ==============================
# START SYSTEM
# ==============================
if __name__ == "__main__":
    print("🔥 Starting FULL BOT SYSTEM...")

    # 🔥 START USER BOTS
    start_all_bots()

    # ==========================
    # THREADS
    # ==========================
    threads = []

    threads.append(threading.Thread(target=run_bot, args=(main_bot, "Main Bot")))
    threads.append(threading.Thread(target=run_bot, args=(admin_bot, "Admin Bot")))
    threads.append(threading.Thread(target=run_bot, args=(receiver_bot, "Receiver Bot")))
    threads.append(threading.Thread(target=run_bot, args=(checker_bot, "Checker Bot")))

    # START ALL
    for t in threads:
        t.start()

    # KEEP ALIVE
    for t in threads:
        t.join()
