import yt_dlp
import os
import uuid
import requests
from io import BytesIO
import re

DOWNLOAD_DIR = "downloads"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# ==============================
# EXPAND URL (STRONG)
# ==============================
def expand_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}

        if any(x in url for x in ["vt.tiktok.com", "vm.tiktok.com", "t.co"]):
            url = requests.get(url, headers=headers, allow_redirects=True, timeout=10).url

        if "x.com" in url:
            url = url.replace("x.com", "twitter.com")

    except Exception as e:
        print("EXPAND ERROR:", e)

    return url


# ==============================
# PLATFORM CHECK
# ==============================
def check_platform(url, platform):
    return (
        (platform == "tiktok" and "tiktok.com" in url) or
        (platform == "instagram" and "instagram.com" in url) or
        (platform == "twitter" and "twitter.com" in url)
    )


# ==============================
# 🔥 TIKTOK (ULTRA FIX)
# ==============================
def tiktok_api(url):
    videos = []
    images = []

    # 1️⃣ tikwm
    try:
        r = requests.get(f"https://tikwm.com/api/?url={url}", timeout=10).json()
        if r.get("data"):
            d = r["data"]

            if d.get("play"):
                videos.append(BytesIO(requests.get(d["play"]).content))

            if d.get("images"):
                for img in d["images"]:
                    images.append(BytesIO(requests.get(img).content))
    except:
        pass

    # 2️⃣ yt-dlp direct fallback
    if not videos and not images:
        try:
            ydl_opts = {"format": "best", "quiet": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info.get("url"):
                    video = requests.get(info["url"]).content
                    videos.append(BytesIO(video))
        except:
            pass

    if videos or images:
        return {"status": True, "videos": videos, "images": images}

    return {"status": False}


# ==============================
# INSTAGRAM (WORKING)
# ==============================
def instagram_api(url):
    try:
        r = requests.get(f"https://igram.world/api/ig?url={url}", timeout=10).json()

        videos = []
        images = []

        if r.get("media"):
            for m in r["media"]:
                data = requests.get(m["url"]).content
                if m.get("type") == "video":
                    videos.append(BytesIO(data))
                else:
                    images.append(BytesIO(data))

        if videos or images:
            return {"status": True, "videos": videos, "images": images}

        return {"status": False}

    except Exception as e:
        print("IG ERROR:", e)
        return {"status": False}


# ==============================
# 🔥 TWITTER/X FIXED
# ==============================
def twitter_api(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(f"https://twitsave.com/info?url={url}", headers=headers).text

        match = re.search(r'href="(https://[^"]+\.mp4[^"]*)"', html)

        if match:
            video_url = match.group(1)
            video = requests.get(video_url).content
            return {"status": True, "videos": [BytesIO(video)], "images": []}

        return {"status": False}

    except Exception as e:
        print("TW ERROR:", e)
        return {"status": False}


# ==============================
# MAIN
# ==============================
def download_video(url, platform):
    try:
        url = expand_url(url)

        if not check_platform(url, platform):
            return {
                "status": False,
                "error": f"This bot allow only {platform} links!"
            }

        # 1️⃣ TRY yt-dlp
        file_id = str(uuid.uuid4())
        base = os.path.join(DOWNLOAD_DIR, file_id)

        videos = []
        images = []

        try:
            ydl_opts = {
                "outtmpl": base + ".%(ext)s",
                "format": "best",
                "quiet": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)

        except:
            pass

        # READ FILES
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(file_id):
                path = os.path.join(DOWNLOAD_DIR, f)
                data = open(path, "rb").read()

                if f.endswith((".mp4", ".webm")):
                    videos.append(BytesIO(data))
                elif f.endswith((".jpg", ".png", ".jpeg")):
                    images.append(BytesIO(data))

        # 2️⃣ FALLBACK
        if not videos and not images:

            if platform == "tiktok":
                return tiktok_api(url)

            elif platform == "instagram":
                return instagram_api(url)

            elif platform == "twitter":
                return twitter_api(url)

        # RESULT
        if videos or images:
            return {"status": True, "videos": videos, "images": images}

        return {"status": False}

    except Exception as e:
        print("MAIN ERROR:", e)
        return {"status": False}
