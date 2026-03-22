import threading
import time
import traceback

# ==============================
# IMPORT BOTS
# ==============================
import main_bot
import admin_bot
import receiver_bot

# USER BOTS MANAGER
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
# USER BOTS (SMART LOADER)
# ==============================
def run_user_bots():
    print("🤖 Starting USER bots system...")

    # 🔥 first load
    try:
        start_all_bots()
    except Exception as e:
        print("❌ Initial user bots error:", e)

    # 🔁 check new bots only
    while True:
        try:
            start_all_bots()
        except Exception as e:
            print("❌ User bots error:", e)

        time.sleep(30)  # 🔥 muhiim (ha ka dhigin 10 sec)


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
    # KEEP SYSTEM ALIVE
    # ==============================
    while True:
        time.sleep(60)
