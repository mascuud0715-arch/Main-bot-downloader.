import threading
import time
import traceback

# IMPORT BOTS
import main_bot
import admin_bot
import receiver_bot

# USER BOTS
from user_bots_manager import start_all_bots


# ==============================
# SAFE RUN FUNCTION
# ==============================
def safe_run(name, func):
    while True:
        try:
            print(f"🚀 Starting {name}...")
            func()
        except Exception as e:
            print(f"❌ {name} crashed:", e)
            traceback.print_exc()
            print(f"🔄 Restarting {name} in 5 sec...")
            time.sleep(5)


# ==============================
# BOT RUNNERS
# ==============================
def run_main():
    safe_run("MAIN BOT", lambda: main_bot.bot.infinity_polling(skip_pending=True))

def run_admin():
    safe_run("ADMIN BOT", lambda: admin_bot.bot.infinity_polling(skip_pending=True))

def run_receiver():
    safe_run("RECEIVER BOT", lambda: receiver_bot.bot.infinity_polling(skip_pending=True))

def run_user_bots():
    while True:
        try:
            print("🤖 Loading USER bots...")
            start_all_bots()
            break
        except Exception as e:
            print("❌ User bots error:", e)
            time.sleep(5)


# ==============================
# START ALL THREADS
# ==============================
if __name__ == "__main__":
    threads = []

    threads.append(threading.Thread(target=run_main, daemon=True))
    threads.append(threading.Thread(target=run_admin, daemon=True))
    threads.append(threading.Thread(target=run_receiver, daemon=True))
    threads.append(threading.Thread(target=run_user_bots, daemon=True))

    for t in threads:
        t.start()
        time.sleep(1)

    print("🔥 ALL SYSTEM RUNNING...")

    # KEEP MAIN THREAD ALIVE (VERY IMPORTANT)
    while True:
        time.sleep(60)
