import yt_dlp
import os
import uuid
import requests

# ==============================
# CREATE DOWNLOAD FOLDER
# ==============================
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# ==============================
# EXPAND SHORT LINKS
# ==============================
def expand_url(url):
    try:
        if any(x in url for x in ["vt.tiktok.com", "vm.tiktok.com", "t.co"]):
            r = requests.get(url, allow_redirects=True, timeout=10)
            return r.url
    except Exception as e:
        print("EXPAND ERROR:", e)
    return url

# ==============================
# TIKTOK API FALLBACK (🔥 muhiim)
# ==============================
def tiktok_api_download(url):
    try:
        api = f"https://tikwm.com/api/?url={url}"
        r = requests.get(api, timeout=10).json()

        if r.get("data"):
            data = r["data"]

            video_url = data.get("play")
            images = data.get("images")

            videos = []
            imgs = []

            # video
            if video_url:
                videos.append(video_url)

            # images (slideshow)
            if images:
                for img in images:
                    imgs.append(img)

            if videos or imgs:
                return {
                    "status": True,
                    "videos": videos,
                    "images": imgs
                }

        return {"status": False}

    except Exception as e:
        print("TIKTOK API ERROR:", e)
        return {"status": False}

# ==============================
# MAIN DOWNLOAD FUNCTION
# ==============================
def download_video(url, platform="unknown"):
    try:
        # expand links
        url = expand_url(url)
        print("FINAL URL:", url)

        file_id = str(uuid.uuid4())
        base_path = os.path.join("downloads", file_id)

        videos = []
        images = []

        # ==============================
        # YT-DLP OPTIONS
        # ==============================
        ydl_opts = {
            "outtmpl": base_path + ".%(ext)s",
            "format": "bestvideo+bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "nocheckcertificate": True,
        }

        info = None

        # ==============================
        # TRY YT-DLP
        # ==============================
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
        except Exception as e:
            print("YTDLP ERROR:", e)

        # ==============================
        # COLLECT FILES
        # ==============================
        for file in os.listdir("downloads"):
            if file.startswith(file_id):
                full_path = os.path.join("downloads", file)

                if file.endswith((".mp4", ".mkv", ".webm")):
                    videos.append(open(full_path, "rb"))

                elif file.endswith((".jpg", ".jpeg", ".png")):
                    images.append(open(full_path, "rb"))

        # ==============================
        # IF YT-DLP FAILED → TIKTOK API
        # ==============================
        if not videos and not images and "tiktok.com" in url:
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

        return {"status": False}

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        return {"status": False}
