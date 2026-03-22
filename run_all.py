import threading
import time

# IMPORT BOTS
from main_bot import bot as main_bot
from admin_bot import bot as admin_bot
from receiver_bot import bot as receiver_bot
from checker_bot import bot as checker_bot

# USER BOTS
from user_bots_manager import start_all_bots, running_bots

# ==============================
# SAFE RUN FUNCTION
# ==============================
def run_bot(bot_instance, name):
    print(f"🚀 {name} started")

    while True:
        try:
            bot_instance.infinity_polling(timeout=30, long_polling_timeout=10)
        except Exception as e:
            print(f"❌ {name} crashed:", e)
            time.sleep(5)

# ==============================
# START USER BOT THREAD
# ==============================
def start_user_bot_thread(token, bot):
    name = f"UserBot-{token[:10]}"

    if hasattr(bot, "is_running"):
        return

    bot.is_running = True

    threading.Thread(
        target=run_bot,
        args=(bot, name),
        daemon=True
    ).start()

    print(f"✅ Started {name}")

# ==============================
# MONITOR NEW USER BOTS
# ==============================
def monitor_user_bots():
    print("👀 Monitoring user bots...")

    while True:
        try:
            # reload bots from DB
            start_all_bots()

            # start new ones
            for token, bot in running_bots.items():
                start_user_bot_thread(token, bot)

        except Exception as e:
            print("❌ Monitor error:", e)

        time.sleep(10)  # check every 10 sec

# ==============================
# START SYSTEM
# ==============================
if __name__ == "__main__":
    print("🔥 STARTING FULL SYSTEM...")

    # 🔥 LOAD USER BOTS FIRST
    start_all_bots()

    # ==========================
    # THREADS LIST
    # ==========================
    threads = []

    # MAIN BOTS
    threads.append(threading.Thread(target=run_bot, args=(main_bot, "Main Bot"), daemon=True))
    threads.append(threading.Thread(target=run_bot, args=(admin_bot, "Admin Bot"), daemon=True))
    threads.append(threading.Thread(target=run_bot, args=(receiver_bot, "Receiver Bot"), daemon=True))
    threads.append(threading.Thread(target=run_bot, args=(checker_bot, "Checker Bot"), daemon=True))

    # USER BOTS (INITIAL START)
    for token, bot in running_bots.items():
        start_user_bot_thread(token, bot)

    # MONITOR THREAD (VERY IMPORTANT 🔥)
    threads.append(threading.Thread(target=monitor_user_bots, daemon=True))

    # ==========================
    # START ALL THREADS
    # ==========================
    for t in threads:
        t.start()

    # KEEP ALIVE
    while True:
        time.sleep(60)
