import threading
import time

# IMPORT BOTS
from main_bot import bot as main_bot
from admin_bot import bot as admin_bot
from receiver_bot import bot as receiver_bot
from checker_bot import bot as checker_bot

# USER BOTS (AUTO THREAD gudaha ayuu ka shaqeeyaa)
from user_bots_manager import start_all_bots

# ==============================
# SAFE RUN FUNCTION
# ==============================
def run_bot(bot_instance, name):
    print(f"🚀 {name} started")

    # 🔥 muhiim: ka saar webhook si looga fogaado 409
    try:
        bot_instance.remove_webhook()
        time.sleep(1)
    except:
        pass

    while True:
        try:
            bot_instance.infinity_polling(
                timeout=60,
                long_polling_timeout=60,
                skip_pending=True
            )
        except Exception as e:
            print(f"❌ {name} crashed:", e)
            time.sleep(5)

# ==============================
# START SYSTEM
# ==============================
if __name__ == "__main__":
    print("🔥 STARTING FULL SYSTEM...")

    # ✅ USER BOTS (HAL MAR KALIYA 🔥)
    start_all_bots()

    # ==========================
    # MAIN THREADS
    # ==========================
    threads = [
        threading.Thread(target=run_bot, args=(main_bot, "Main Bot"), daemon=True),
        threading.Thread(target=run_bot, args=(admin_bot, "Admin Bot"), daemon=True),
        threading.Thread(target=run_bot, args=(receiver_bot, "Receiver Bot"), daemon=True),
        threading.Thread(target=run_bot, args=(checker_bot, "Checker Bot"), daemon=True),
    ]

    # ==========================
    # START THREADS
    # ==========================
    for t in threads:
        t.start()

    # ==========================
    # KEEP ALIVE
    # ==========================
    while True:
        time.sleep(60)
