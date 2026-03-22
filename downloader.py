import yt_dlp
import os
import uuid

# ==============================
# DOWNLOAD FUNCTION
# ==============================
def download_video(url, platform="Unknown"):
    try:
        # unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.mp4"

        # download path
        output_path = os.path.join("downloads", filename)

        # create folder if not exists
        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        # yt-dlp options
        ydl_opts = {
            "outtmpl": output_path,
            "format": "mp4/best",
            "noplaylist": True,
            "quiet": True,
            "nocheckcertificate": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # check file exists
        if os.path.exists(output_path):
            return {
                "status": True,
                "video": open(output_path, "rb")
            }

        return {"status": False}

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
        return {"status": False}
