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
# EXPAND SHORT LINKS (TikTok/X)
# ==============================
def expand_url(url):
    try:
        if "vt.tiktok.com" in url or "vm.tiktok.com" in url or "t.co" in url:
            r = requests.get(url, allow_redirects=True, timeout=10)
            return r.url
    except:
        pass
    return url

# ==============================
# MAIN DOWNLOAD FUNCTION
# ==============================
def download_video(url, platform="unknown"):
    try:
        # 🔥 expand short links
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

        # ==============================
        # DOWNLOAD
        # ==============================
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

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
