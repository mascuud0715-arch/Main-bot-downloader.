from pymongo import MongoClient
from config import MONGO_URI

# ==============================
# CONNECT DB
# ==============================
client = MongoClient(MONGO_URI)
db = client["bot_system"]

bots_col = db["bots"]
users_col = db["users"]
stats_col = db["stats"]
settings_col = db["settings"]

# ==============================
# USERS
# ==============================
def add_user(user_id):
    try:
        users_col.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id}},
            upsert=True
        )
    except Exception as e:
        print("DB USER ERROR:", e)

def get_users_count():
    try:
        return users_col.count_documents({})
    except:
        return 0

# ==============================
# DOWNLOAD STATS
# ==============================
def add_download(user_id, platform):
    try:
        stats_col.update_one(
            {"platform": platform},
            {"$inc": {"count": 1}},
            upsert=True
        )
    except Exception as e:
        print("DB DOWNLOAD ERROR:", e)

def get_all_stats():
    try:
        return list(stats_col.find())
    except:
        return []

# ==============================
# BOTS
# ==============================
def add_bot(token, platform):
    try:
        bots_col.update_one(
            {"token": token},
            {"$set": {
                "token": token,
                "platform": platform
            }},
            upsert=True
        )
    except Exception as e:
        print("DB ADD BOT ERROR:", e)

def get_all_bots():
    try:
        return list(bots_col.find())
    except Exception as e:
        print("DB GET BOTS ERROR:", e)
        return []

def delete_bot(token):
    try:
        bots_col.delete_one({"token": token})
    except Exception as e:
        print("DB DELETE BOT ERROR:", e)

# ==============================
# SETTINGS
# ==============================
def set_setting(key, value):
    try:
        settings_col.update_one(
            {"key": key},
            {"$set": {"value": value}},
            upsert=True
        )
    except Exception as e:
        print("DB SETTING ERROR:", e)

def get_setting(key):
    try:
        s = settings_col.find_one({"key": key})
        return s["value"] if s else "ON"
    except:
        return "ON"
