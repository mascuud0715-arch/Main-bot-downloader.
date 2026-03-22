import os

# ==============================
# BOT TOKENS
# ==============================
MAIN_BOT_TOKEN = os.getenv("MAIN_BOT_TOKEN")
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")
RECEIVER_BOT_TOKEN = os.getenv("RECEIVER_BOT_TOKEN")

# ==============================
# ADMIN
# ==============================
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# ==============================
# DATABASE
# ==============================
MONGO_URI = os.getenv("MONGO_URI")

# ==============================
# VALIDATION (IMPORTANT 🔥)
# ==============================
if not MAIN_BOT_TOKEN:
    raise Exception("MAIN_BOT_TOKEN is missing")

if not ADMIN_BOT_TOKEN:
    raise Exception("ADMIN_BOT_TOKEN is missing")

if not RECEIVER_BOT_TOKEN:
    raise Exception("RECEIVER_BOT_TOKEN is missing")

if not MONGO_URI:
    raise Exception("MONGO_URI is missing")

if ADMIN_ID == 0:
    raise Exception("ADMIN_ID is missing or invalid")
