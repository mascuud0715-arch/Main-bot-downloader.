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
def check_platform(url, platform):
    if platform == "tiktok":
        return "tiktok.com" in url

    elif platform == "instagram":
        return "instagram.com" in url

    elif platform == "twitter":
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
                v = requests.get(d["play"]).content
                videos.append(BytesIO(v))

            # IMAGES
            if d.get("images"):
                for img in d["images"]:
                    i = requests.get(img).content
                    images.append(BytesIO(i))

        if videos or images:
            return {"status": True, "videos": videos, "images": images}

        return {"status": False}

    except Exception as e:
        print("TT API ERROR:", e)
        return {"status": False}


# ==============================
# INSTAGRAM API
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
# TWITTER/X API (🔥 muhiim)
# ==============================
def twitter_api(url):
    try:
        api = f"https://twitsave.com/info?url={url}"
        res = requests.get(api, timeout=10).json()

        videos = []

        if res.get("links"):
            for v in res["links"]:
                link = v.get("url")
                if link:
                    data = requests.get(link).content
                    videos.append(BytesIO(data))
                    break  # hal video ku filan

        if videos:
            return {"status": True, "videos": videos, "images": []}

        return {"status": False}

    except Exception as e:
        print("TW API ERROR:", e)
        return {"status": False}


# ==============================
# MAIN DOWNLOAD FUNCTION
# ==============================
def download_video(url, platform):
    try:
        url = expand_url(url)
        print("URL:", url)
        print("PLATFORM:", platform)

        # 🔒 PLATFORM LOCK
        if not check_platform(url, platform):
            return {
                "status": False,
                "error": f"This bot allow only {platform} links!"
            }

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
                "nocheckcertificate": True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)

        except Exception as e:
            print("YTDLP ERROR:", e)

        # ==============================
        # READ FILES
        # ==============================
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(file_id):
                path = os.path.join(DOWNLOAD_DIR, f)

                try:
                    with open(path, "rb") as file:
                        data = file.read()

                    if f.endswith((".mp4", ".webm", ".mkv")):
                        videos.append(BytesIO(data))

                    elif f.endswith((".jpg", ".jpeg", ".png")):
                        images.append(BytesIO(data))

                except Exception as e:
                    print("READ ERROR:", e)

        # ==============================
        # 2️⃣ FALLBACK SYSTEM
        # ==============================

        if not videos and not images:

            if platform == "tiktok":
                return tiktok_api(url)

            elif platform == "instagram":
                return instagram_api(url)

            elif platform == "twitter":
                return twitter_api(url)

        # ==============================
        # RESULT
        # ==============================
        if videos or images:
            return {
                "status": True,
                "videos": videos,
                "images": images
            }

        return {"status": False}

    except Exception as e:
        print("MAIN ERROR:", e)
        return {"status": False}
