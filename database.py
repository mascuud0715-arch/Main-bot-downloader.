import os
from pymongo import MongoClient
from datetime import datetime

# ==============================
# CONNECT DATABASE (RAILWAY ENV)
# ==============================
MONGO_URL = os.getenv("MONGO_URI")

if not MONGO_URL:
    raise Exception("❌ MONGO_URL is not set in environment variables")

client = MongoClient(MONGO_URL)

# TEST CONNECTION
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
    if not users.find_one({"user_id": user_id}):
        users.insert_one({
            "user_id": user_id,
            "joined": datetime.utcnow()
        })

def get_all_users():
    return list(users.find())

def get_all_users_global():
    user_ids = set()

    # users collection
    for u in users.find():
        user_ids.add(u.get("user_id"))

    # bots collection (haddii user bots leeyihiin users)
    for b in bots.find():
        if "user_id" in b:
            user_ids.add(b.get("user_id"))

    return list(user_ids)

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

# ==============================
# HEALTH CHECK
# ==============================
def ping_db():
    try:
        client.admin.command("ping")
        return True
    except:
        return False
