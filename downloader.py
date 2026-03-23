import yt_dlp
import os
import uuid
import requests
from io import BytesIO

DOWNLOAD_DIR = "downloads"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ==============================
# EXPAND URL
# ==============================
def expand_url(url):
    try:
        if any(x in url for x in ["vt.tiktok.com", "vm.tiktok.com", "t.co"]):
            url = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=15).url

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
# 🔥 TIKTOK (SUPER STABLE)
# ==============================
def tiktok_api(url):
    try:
        videos = []
        images = []

        api = f"https://tikwm.com/api/?url={url}"
        r = requests.get(api, headers=HEADERS, timeout=15).json()

        if r.get("data"):
            d = r["data"]

            # VIDEO
            if d.get("play"):
                video = requests.get(d["play"], headers=HEADERS, timeout=15).content
                videos.append(BytesIO(video))

            # SLIDESHOW
            if d.get("images"):
                for img in d["images"]:
                    image = requests.get(img, headers=HEADERS, timeout=15).content
                    images.append(BytesIO(image))

        if videos or images:
            return {"status": True, "videos": videos, "images": images}

        return {"status": False}

    except Exception as e:
        print("TT ERROR:", e)
        return {"status": False}


# ==============================
# 🔥 TWITTER/X (NEW API)
# ==============================
def twitter_api(url):
    try:
        videos = []

        api = f"https://api.savetwitter.net/api/twitter/video?url={url}"
        r = requests.get(api, headers=HEADERS, timeout=15).json()

        if r.get("data"):
            for v in r["data"]:
                link = v.get("url")
                if link:
                    video = requests.get(link, headers=HEADERS, timeout=15).content
                    videos.append(BytesIO(video))
                    break

        if videos:
            return {"status": True, "videos": videos, "images": []}

        return {"status": False}

    except Exception as e:
        print("TW ERROR:", e)
        return {"status": False}


# ==============================
# INSTAGRAM
# ==============================
def instagram_api(url):
    try:
        r = requests.get(f"https://igram.world/api/ig?url={url}", headers=HEADERS, timeout=15).json()

        videos = []
        images = []

        if r.get("media"):
            for m in r["media"]:
                data = requests.get(m["url"], headers=HEADERS, timeout=15).content
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
# MAIN FUNCTION
# ==============================
def download_video(url, platform):
    try:
        url = expand_url(url)

        print("URL:", url)
        print("PLATFORM:", platform)

        if not check_platform(url, platform):
            return {
                "status": False,
                "error": f"This bot allow only {platform} links!"
            }

        # 🔥 DIRECT API FIRST (IMPORTANT)
        if platform == "tiktok":
            res = tiktok_api(url)
            if res["status"]:
                return res

        elif platform == "twitter":
            res = twitter_api(url)
            if res["status"]:
                return res

        elif platform == "instagram":
            res = instagram_api(url)
            if res["status"]:
                return res

        # ==============================
        # yt-dlp fallback
        # ==============================
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

        except Exception as e:
            print("YTDLP ERROR:", e)

        # READ FILES
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(file_id):
                path = os.path.join(DOWNLOAD_DIR, f)
                data = open(path, "rb").read()

                if f.endswith((".mp4", ".webm")):
                    videos.append(BytesIO(data))

                elif f.endswith((".jpg", ".png", ".jpeg")):
                    images.append(BytesIO(data))

        if videos or images:
            return {"status": True, "videos": videos, "images": images}

        return {"status": False}

    except Exception as e:
        print("MAIN ERROR:", e)
        return {"status": False}
