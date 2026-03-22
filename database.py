from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["telegram_bot_system"]

users = db["users"]
bots = db["bots"]
settings = db["settings"]
channels = db["channels"]
downloads = db["downloads"]

# ==============================
# USERS
# ==============================
def add_user(user_id, username):
    if not users.find_one({"user_id": user_id}):
        users.insert_one({
            "user_id": user_id,
            "username": username
        })

def get_all_users():
    return list(users.find())

# ==============================
# BOTS
# ==============================
def add_bot(user_id, token, platform):
    bots.insert_one({
        "user_id": user_id,
        "token": token,
        "platform": platform
    })

def get_all_bots():
    return list(bots.find())

def get_user_bots(user_id):
    return list(bots.find({"user_id": user_id}))

def delete_bot(token):
    bots.delete_one({"token": token})

# ==============================
# SETTINGS
# ==============================
def set_setting(key, value):
    settings.update_one(
        {"key": key},
        {"$set": {"value": value}},
        upsert=True
    )

def get_setting(key, default=None):
    data = settings.find_one({"key": key})
    return data["value"] if data else default

# ==============================
# GET CHANNELS
# ==============================
def get_channels():
    data = db.settings.find_one({"type": "channels"})
    
    if data and "channels" in data:
        return data["channels"]
    
    return []

# ==============================
# DOWNLOAD STATS
# ==============================
def add_download(platform):
    downloads.insert_one({"platform": platform})

def get_download_count():
    return downloads.count_documents({})

def get_platform_stats():
    return list(downloads.aggregate([
        {"$group": {"_id": "$platform", "count": {"$sum": 1}}}
    ]))
