from fastapi import FastAPI, Depends, HTTPException, Header
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY is missing in .env file!")

async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True

@app.post("/fetch_video")
async def fetch_video(data: dict, auth: bool = Depends(verify_api_key)):
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Missing URL")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "age_limit": 99,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get("url")
        
        if not video_url:
            raise HTTPException(status_code=404, detail="Failed to fetch video URL")

        return {"video_url": video_url}

    except yt_dlp.DownloadError as e:
        raise HTTPException(status_code=500, detail=f"yt-dlp error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
