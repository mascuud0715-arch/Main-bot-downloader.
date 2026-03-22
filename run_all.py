import threading
import time

# import bots
from main_bot import bot as main_bot
from admin_bot import bot as admin_bot
from receiver_bot import bot as receiver_bot
from checker_bot import bot as checker_bot

# user bots
from user_bots_manager import start_all_bots


# ==============================
# SAFE POLLING
# ==============================
def run_bot(bot_instance, name):
    print(f"🚀 {name} started")

    while True:
        try:
            bot_instance.infinity_polling(
                timeout=60,
                long_polling_timeout=30,
                skip_pending=True
            )
        except Exception as e:
            print(f"❌ {name} crashed: {e}")
            time.sleep(5)


# ==============================
# START SYSTEM
# ==============================
if __name__ == "__main__":
    print("🔥 Starting FULL BOT SYSTEM...")

    # 🔥 USER BOTS (THREAD GOONI AH)
    user_thread = threading.Thread(target=start_all_bots)
    user_thread.daemon = True
    user_thread.start()

    time.sleep(2)

    # ==========================
    # SYSTEM BOTS
    # ==========================
    bots_threads = [
        threading.Thread(target=run_bot, args=(main_bot, "Main Bot")),
        threading.Thread(target=run_bot, args=(admin_bot, "Admin Bot")),
        threading.Thread(target=run_bot, args=(receiver_bot, "Receiver Bot")),
        threading.Thread(target=run_bot, args=(checker_bot, "Checker Bot")),
    ]

    # START THREADS
    for t in bots_threads:
        t.daemon = True
        t.start()

    # KEEP ALIVE (MUHIIM)
    while True:
        time.sleep(10)
