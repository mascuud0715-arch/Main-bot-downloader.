import requests

# ==============================
# TIKTOK DOWNLOADER
# ==============================
def download_tiktok(url):
    try:
        api = f"https://tikwm.com/api/?url={url}"
        res = requests.get(api).json()

        video = res["data"]["play"]
        return {
            "status": True,
            "video": video
        }

    except Exception as e:
        return {
            "status": False,
            "error": str(e)
        }

# ==============================
# INSTAGRAM DOWNLOADER
# ==============================
def download_instagram(url):
    try:
        api = f"https://api.vevioz.com/api/button/mp4?url={url}"

        return {
            "status": True,
            "video": api
        }

    except Exception as e:
        return {
            "status": False,
            "error": str(e)
        }

# ==============================
# X (TWITTER) DOWNLOADER
# ==============================
def download_x(url):
    try:
        # simple placeholder (waxaad badali kartaa API kale)
        return {
            "status": True,
            "video": url
        }

    except Exception as e:
        return {
            "status": False,
            "error": str(e)
        }

# ==============================
# UNIVERSAL DOWNLOADER
# ==============================
def download_video(url, platform):
    if platform == "TikTok":
        return download_tiktok(url)

    elif platform == "Instagram":
        return download_instagram(url)

    elif platform == "X":
        return download_x(url)

    else:
        return {
            "status": False,
            "error": "Unsupported platform"
        }
