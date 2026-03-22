from pymongo import MongoClient
from datetime import datetime

# ==============================
# CONNECT DATABASE
# ==============================
MONGO_URL = "YOUR_MONGO_URL_HERE"

client = MongoClient(MONGO_URL)
db = client["telegram_bot_system"]

# ==============================
# COLLECTIONS
# ==============================
users = db["users"]
bots = db["bots"]
channels = db["channels"]
settings = db["settings"]
downloads = db["downloads"]

# ==============================
# USERS
# ==============================
def add_user(user_id):
    if not users.find_one({"user_id": user_id}):
        users.insert_one({
            "user_id": user_id,
            "joined": datetime.utcnow()
        })

def get_all_users():
    return list(users.find())

# ==============================
# BOTS
# ==============================
def add_bot(user_id, token, username, platform):
    if not bots.find_one({"token": token}):
        bots.insert_one({
            "user_id": user_id,
            "token": token,
            "username": username,
            "platform": platform,
            "created_at": datetime.utcnow()
        })

def get_all_bots():
    return list(bots.find())

def remove_bot(user_id, username):
    return bots.delete_one({
        "user_id": user_id,
        "username": username
    })

# ==============================
# SETTINGS (SYSTEM CONTROL)
# ==============================
def set_setting(key, value):
    settings.update_one(
        {"key": key},
        {"$set": {"value": value}},
        upsert=True
    )

def get_setting(key):
    s = settings.find_one({"key": key})
    return s["value"] if s else None

# ==============================
# DOWNLOAD TRACKING
# ==============================
def add_download(platform):
    downloads.insert_one({
        "platform": platform,
        "time": datetime.utcnow()
    })

def get_download_count():
    return downloads.count_documents({})

def get_platform_stats():
    return list(downloads.aggregate([
        {"$group": {"_id": "$platform", "count": {"$sum": 1}}}
    ]))
