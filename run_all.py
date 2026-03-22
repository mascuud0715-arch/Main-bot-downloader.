import threading
import time
import traceback

# ==============================
# IMPORT ALL BOTS
# ==============================
import main_bot
import admin_bot
import receiver_bot

# USER BOTS
from user_bots_manager import start_all_bots


# ==============================
# SAFE RUN (AUTO RESTART)
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
# MAIN BOT
# ==============================
def run_main():
    safe_run(
        "MAIN BOT",
        lambda: main_bot.bot.infinity_polling(skip_pending=True)
    )


# ==============================
# ADMIN BOT
# ==============================
def run_admin():
    safe_run(
        "ADMIN BOT",
        lambda: admin_bot.bot.infinity_polling(skip_pending=True)
    )


# ==============================
# RECEIVER BOT
# ==============================
def run_receiver():
    safe_run(
        "RECEIVER BOT",
        lambda: receiver_bot.bot.infinity_polling(skip_pending=True)
    )


# ==============================
# USER BOTS (AUTO LOAD + LOOP)
# ==============================
def run_user_bots():
    while True:
        try:
            print("🤖 Checking USER bots...")
            start_all_bots()
        except Exception as e:
            print("❌ User bots error:", e)

        time.sleep(10)  # 🔥 check every 10 seconds


# ==============================
# START SYSTEM
# ==============================
if __name__ == "__main__":
    print("🔥 Starting FULL SYSTEM...")

    threads = []

    t1 = threading.Thread(target=run_main, daemon=True)
    t2 = threading.Thread(target=run_admin, daemon=True)
    t3 = threading.Thread(target=run_receiver, daemon=True)
    t4 = threading.Thread(target=run_user_bots, daemon=True)

    threads.extend([t1, t2, t3, t4])

    for t in threads:
        t.start()
        time.sleep(1)

    print("✅ ALL BOTS ARE RUNNING 🚀")

    # ==============================
    # KEEP SYSTEM ALIVE (IMPORTANT)
    # ==============================
    while True:
        time.sleep(60)
