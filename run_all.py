import threading
import time
import traceback

# ==============================
# IMPORT BOTS
# ==============================
import main_bot
import admin_bot
import receiver_bot
import support_bot

# USER BOT SYSTEM
from user_bots_manager import (
    start_user_bot,
    running_bots,
    bot_tokens
)

from database import get_all_bots


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
# SUPPORT
# ==============================
def run_support():
    safe_run(
        "SUPPORT BOT",
        support_bot.run
    )

# ==============================
# 🔥 STOP REMOVED BOTS
# ==============================
def stop_removed_bots(db_tokens):
    for username, bot in list(running_bots.items()):
        token = bot_tokens.get(username)

        # haddii token DB ku jirin → STOP
        if token not in db_tokens:
            try:
                bot.stop_polling()
                print(f"🛑 Stopped removed bot @{username}")
            except Exception as e:
                print("STOP ERROR:", e)

            running_bots.pop(username, None)
            bot_tokens.pop(username, None)


# ==============================
# USER BOTS SYSTEM (SMART)
# ==============================
def run_user_bots():
    print("🤖 Starting USER bots system...")

    loaded_tokens = set()

    while True:
        try:
            all_bots = get_all_bots()

            # 🔥 tokens DB
            db_tokens = set()
            for b in all_bots:
                if b.get("token"):
                    db_tokens.add(b.get("token"))

            # 🔴 STOP removed bots
            stop_removed_bots(db_tokens)

            # 🟢 START new bots only
            for b in all_bots:
                token = b.get("token")
                platform = b.get("platform")

                if not token:
                    continue

                if token in loaded_tokens:
                    continue

                start_user_bot(token, platform)
                loaded_tokens.add(token)

        except Exception as e:
            print("❌ User bots error:", e)

        time.sleep(30)


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
    t5 = threading.Thread(target=run_support, daemon=True)

    threads.extend([t1, t2, t3, t4, t5])

    for t in threads:
        t.start()
        time.sleep(1)

    print("✅ ALL BOTS ARE RUNNING 🚀")

    # ==============================
    # KEEP SYSTEM ALIVE
    # ==============================
    while True:
        time.sleep(60)
