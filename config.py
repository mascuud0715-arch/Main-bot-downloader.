import os

# ==============================
# BOT TOKENS
# ==============================
MAIN_BOT_TOKEN = os.getenv("MAIN_BOT_TOKEN")
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")
CHECKER_BOT_TOKEN = os.getenv("CHECKER_BOT_TOKEN")
RECEIVER_BOT_TOKEN = os.getenv("RECEIVER_BOT_TOKEN")

# ==============================
# DATABASE
# ==============================
MONGO_URI = os.getenv("MONGO_URI")

# ==============================
# ADMIN
# ==============================
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# ==============================
# SYSTEM CONTROL
# ==============================
SYSTEM_STATUS = os.getenv("SYSTEM_STATUS", "ON")  # ON / OFF
RECEIVER_STATUS = os.getenv("RECEIVER_STATUS", "OFF")  # ON / OFF

# ==============================
# DEFAULT SETTINGS
# ==============================
DEFAULT_CAPTION = "Created: @Create_Our_own_bot"

# ==============================
# VALIDATION (IMPORTANT)
# ==============================
def validate_config():
    missing = []

    if not MAIN_BOT_TOKEN:
        missing.append("MAIN_BOT_TOKEN")

    if not ADMIN_BOT_TOKEN:
        missing.append("ADMIN_BOT_TOKEN")

    if not CHECKER_BOT_TOKEN:
        missing.append("CHECKER_BOT_TOKEN")

    if not RECEIVER_BOT_TOKEN:
        missing.append("RECEIVER_BOT_TOKEN")

    if not MONGO_URI:
        missing.append("MONGO_URI")

    if ADMIN_ID == 0:
        missing.append("ADMIN_ID")

    if missing:
        raise Exception(f"Missing ENV variables: {', '.join(missing)}")

# Run validation on import
validate_config()
