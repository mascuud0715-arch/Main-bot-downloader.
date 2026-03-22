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
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
except:
    ADMIN_ID = 0

# ==============================
# DATABASE
# ==============================
MONGO_URI = os.getenv("MONGO_URI")

# ==============================
# VALIDATION (IMPORTANT 🔥)
# ==============================
def validate_config():
    errors = []

    if not MAIN_BOT_TOKEN:
        errors.append("MAIN_BOT_TOKEN missing")

    if not ADMIN_BOT_TOKEN:
        errors.append("ADMIN_BOT_TOKEN missing")

    if not RECEIVER_BOT_TOKEN:
        errors.append("RECEIVER_BOT_TOKEN missing")

    if not MONGO_URI:
        errors.append("MONGO_URI missing")

    if ADMIN_ID == 0:
        errors.append("ADMIN_ID invalid")

    if errors:
        for e in errors:
            print("❌", e)
        raise Exception("CONFIG ERROR ❌")

    print("✅ Config loaded successfully")

# RUN VALIDATION
validate_config()
