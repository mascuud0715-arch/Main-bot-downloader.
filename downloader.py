import yt_dlp
import os
import uuid
import requests
from io import BytesIO

DOWNLOAD_DIR = "downloads"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# ==============================
# EXPAND URL
# ==============================
def expand_url(url):
    try:
        if any(x in url for x in ["vt.tiktok.com", "vm.tiktok.com", "t.co"]):
            url = requests.get(url, allow_redirects=True, timeout=10).url

        if "x.com" in url:
            url = url.replace("x.com", "twitter.com")

    except Exception as e:
        print("EXPAND ERROR:", e)

    return url

# ==============================
# PLATFORM CHECK
# ==============================
def is_valid(url, platform):
    if platform == "tiktok":
        return "tiktok.com" in url
    if platform == "instagram":
        return "instagram.com" in url
    if platform == "twitter":
        return "twitter.com" in url
    return False

# ==============================
# TIKTOK API (VIDEO + IMAGES)
# ==============================
def tiktok_api(url):
    try:
        api = f"https://tikwm.com/api/?url={url}"
        res = requests.get(api, timeout=10).json()

        videos = []
        images = []

        if res.get("data"):
            d = res["data"]

            # VIDEO
            if d.get("play"):
                videos.append(BytesIO(requests.get(d["play"]).content))

            # IMAGES (🔥 muhiim)
            if d.get("images"):
                for img in d["images"]:
                    images.append(BytesIO(requests.get(img).content))

        if videos or images:
            return {"status": True, "videos": videos, "images": images}

        return {"status": False}

    except Exception as e:
        print("TT API ERROR:", e)
        return {"status": False}

# ==============================
# INSTAGRAM API (🔥 FIX)
# ==============================
def instagram_api(url):
    try:
        api = f"https://igram.world/api/ig?url={url}"
        res = requests.get(api, timeout=10).json()

        videos = []
        images = []

        if res.get("media"):
            for m in res["media"]:
                link = m.get("url")
                if not link:
                    continue

                data = requests.get(link).content

                if m.get("type") == "video":
                    videos.append(BytesIO(data))
                else:
                    images.append(BytesIO(data))

        if videos or images:
            return {"status": True, "videos": videos, "images": images}

        return {"status": False}

    except Exception as e:
        print("IG API ERROR:", e)
        return {"status": False}

# ==============================
# MAIN FUNCTION
# ==============================
def download_video(url, platform):
    try:
        url = expand_url(url)
        print("URL:", url, "| PLATFORM:", platform)

        # 🔒 PLATFORM LOCK
        if not is_valid(url, platform):
            return {"status": False}

        videos = []
        images = []

        # ==============================
        # 1️⃣ TRY YT-DLP
        # ==============================
        file_id = str(uuid.uuid4())
        base = os.path.join(DOWNLOAD_DIR, file_id)

        try:
            ydl_opts = {
                "outtmpl": base + ".%(ext)s",
                "format": "best",
                "quiet": True,
                "noplaylist": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)

        except Exception as e:
            print("YTDLP FAIL:", e)

        # READ FILES
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(file_id):
                p = os.path.join(DOWNLOAD_DIR, f)
                data = open(p, "rb").read()

                if f.endswith((".mp4", ".webm")):
                    videos.append(BytesIO(data))
                elif f.endswith((".jpg", ".png", ".jpeg")):
                    images.append(BytesIO(data))

        # ==============================
        # 2️⃣ PLATFORM FALLBACKS
        # ==============================

        # 🔥 TIKTOK FIX
        if platform == "tiktok" and not videos and not images:
            return tiktok_api(url)

        # 🔥 INSTAGRAM FIX
        if platform == "instagram" and not videos and not images:
            return instagram_api(url)

        # ==============================
        # RESULT
        # ==============================
        if videos or images:
            return {"status": True, "videos": videos, "images": images}

        return {"status": False}

    except Exception as e:
        print("ERROR:", e)
        return {"status": False}
