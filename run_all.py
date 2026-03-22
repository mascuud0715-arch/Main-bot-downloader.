import threading
import time

# IMPORT BOTS
import main_bot
import admin_bot
import receiver_bot

# USER BOTS MANAGER
from user_bots_manager import start_all_bots


# ==============================
# THREAD RUNNER
# ==============================
def run_main():
    print("🚀 Starting MAIN bot...")
    main_bot.bot.infinity_polling(skip_pending=True)

def run_admin():
    print("🛠 Starting ADMIN bot...")
    admin_bot.bot.infinity_polling(skip_pending=True)

def run_receiver():
    print("📡 Starting RECEIVER bot...")
    receiver_bot.bot.infinity_polling(skip_pending=True)

def run_user_bots():
    print("🤖 Loading USER bots...")
    start_all_bots()


# ==============================
# START ALL
# ==============================
if __name__ == "__main__":
    t1 = threading.Thread(target=run_main)
    t2 = threading.Thread(target=run_admin)
    t3 = threading.Thread(target=run_receiver)
    t4 = threading.Thread(target=run_user_bots)

    t1.start()
    time.sleep(1)

    t2.start()
    time.sleep(1)

    t3.start()
    time.sleep(1)

    t4.start()

    print("🔥 ALL SYSTEM RUNNING...")
