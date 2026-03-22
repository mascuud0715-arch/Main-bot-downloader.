import os
from pymongo import MongoClient
from datetime import datetime

# ==============================
# CONNECT DATABASE
# ==============================
MONGO_URL = os.getenv("MONGO_URI")

if not MONGO_URL:
    raise Exception("❌ MONGO_URI is not set")

client = MongoClient(MONGO_URL)

try:
    client.server_info()
    print("✅ MongoDB Connected Successfully")
except Exception as e:
    print("❌ MongoDB Connection Failed:", e)

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
    users.update_one(
        {"user_id": user_id},
        {
            "$setOnInsert": {
                "joined": datetime.utcnow()
            }
        },
        upsert=True
    )

# 🔥 SAVE USER + BOT (MUHIIM)
def save_user_bot(user_id, bot_token):
    users.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "bot_token": bot_token,
                "last_seen": datetime.utcnow()
            },
            "$setOnInsert": {
                "joined": datetime.utcnow()
            }
        },
        upsert=True
    )

def get_all_users():
    return list(users.find())

def get_all_users_global():
    return [u.get("user_id") for u in users.find() if u.get("user_id")]

# 🔥 CORE: USERS GROUPED BY BOT (BROADCAST)
def get_users_by_bot():
    data = {}

    for u in users.find():
        token = u.get("bot_token")
        uid = u.get("user_id")

        if not token or not uid:
            continue

        if token not in data:
            data[token] = []

        data[token].append(uid)

    return data

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

def get_user_bots(user_id):
    return list(bots.find({"user_id": user_id}))

def remove_bot(user_id, username):
    return bots.delete_one({
        "user_id": user_id,
        "username": username
    })

def get_bot_by_token(token):
    return bots.find_one({"token": token})

# ==============================
# CHANNELS
# ==============================
def add_channel(channel_id):
    if not channels.find_one({"channel_id": channel_id}):
        channels.insert_one({
            "channel_id": channel_id,
            "added_at": datetime.utcnow()
        })

def get_channels():
    return [c.get("channel_id") for c in channels.find()]

def clear_channels():
    channels.delete_many({})

# ==============================
# SETTINGS
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

# ==============================
# HEALTH CHECK
# ==============================
def ping_db():
    try:
        client.admin.command("ping")
        return True
    except:
        return False
