import yt_dlp
import os
import uuid
import requests
from io import BytesIO

# ==============================
# CREATE DOWNLOAD FOLDER
# ==============================
DOWNLOAD_DIR = "downloads"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# ==============================
# EXPAND SHORT LINKS
# ==============================
def expand_url(url):
    try:
        if any(x in url for x in ["vt.tiktok.com", "vm.tiktok.com", "t.co"]):
            r = requests.get(url, allow_redirects=True, timeout=10)
            url = r.url

        # FIX X → Twitter
        if "x.com" in url:
            url = url.replace("x.com", "twitter.com")

    except Exception as e:
        print("EXPAND ERROR:", e)

    return url

# ==============================
# TIKTOK API FALLBACK (SAFE)
# ==============================
def tiktok_api_download(url):
    try:
        api = f"https://tikwm.com/api/?url={url}"
        r = requests.get(api, timeout=10).json()

        if r.get("data"):
            data = r["data"]

            videos = []
            images = []

            # VIDEO
            if data.get("play"):
                video_data = requests.get(data["play"], timeout=10).content
                videos.append(BytesIO(video_data))

            # IMAGES (slideshow)
            if data.get("images"):
                for img_url in data["images"]:
                    img_data = requests.get(img_url, timeout=10).content
                    images.append(BytesIO(img_data))

            if videos or images:
                return {
                    "status": True,
                    "videos": videos,
                    "images": images
                }

        return {"status": False}

    except Exception as e:
        print("TIKTOK API ERROR:", e)
        return {"status": False}

# ==============================
# PLATFORM CHECK (VERY STRONG 🔒)
# ==============================
def is_valid_platform(url, platform):
    if platform == "tiktok":
        return "tiktok.com" in url

    elif platform == "instagram":
        return "instagram.com" in url

    elif platform == "twitter":
        return "twitter.com" in url

    return False

# ==============================
# MAIN DOWNLOAD FUNCTION
# ==============================
def download_video(url, platform="unknown"):
    try:
        # ==============================
        # EXPAND URL
        # ==============================
        url = expand_url(url)
        print("FINAL URL:", url)
        print("PLATFORM:", platform)

        # ==============================
        # 🔒 HARD PLATFORM LOCK
        # ==============================
        if not is_valid_platform(url, platform):
            print("BLOCKED: WRONG PLATFORM")
            return {"status": False}

        # ==============================
        # FILE SETUP
        # ==============================
        file_id = str(uuid.uuid4())
        base_path = os.path.join(DOWNLOAD_DIR, file_id)

        videos = []
        images = []

        # ==============================
        # YT-DLP OPTIONS
        # ==============================
        ydl_opts = {
            "outtmpl": base_path + ".%(ext)s",
            "format": "best",
            "noplaylist": True,
            "quiet": True,
            "nocheckcertificate": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0"
            }
        }

        # ==============================
        # TRY YT-DLP
        # ==============================
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)
        except Exception as e:
            print("YTDLP ERROR:", e)

        # ==============================
        # COLLECT FILES
        # ==============================
        for file in os.listdir(DOWNLOAD_DIR):
            if file.startswith(file_id):
                full_path = os.path.join(DOWNLOAD_DIR, file)

                try:
                    with open(full_path, "rb") as f:
                        data = f.read()

                    if file.endswith((".mp4", ".mkv", ".webm")):
                        videos.append(BytesIO(data))

                    elif file.endswith((".jpg", ".jpeg", ".png")):
                        images.append(BytesIO(data))

                except Exception as e:
                    print("FILE READ ERROR:", e)

        # ==============================
        # 🔥 SAFE TIKTOK FALLBACK (LOCKED)
        # ==============================
        if (
            platform == "tiktok"
            and "tiktok.com" in url
            and not videos
            and not images
        ):
            print("Using TikTok API fallback...")
            return tiktok_api_download(url)

        # ==============================
        # RESULT
        # ==============================
        if videos or images:
            return {
                "status": True,
                "videos": videos,
                "images": images
            }

        print("NO MEDIA FOUND")
        return {"status": False}

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        return {"status": False}
