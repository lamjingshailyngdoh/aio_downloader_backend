from fastapi import FastAPI, Depends, HTTPException, Header
import yt_dlp
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API key
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    logger.error("API_KEY is missing in the .env file!")
    raise ValueError("API_KEY is missing in .env file!")

# API key verification function
async def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key is required")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return True

@app.post("/fetch_video")
async def fetch_video(data: dict, auth: bool = Depends(verify_api_key)):
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Missing URL")

    logger.info(f"Fetching video from URL: {url}")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "age_limit": 99,
        "socket_timeout": 10,  # Prevents hanging requests
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get("url")

        if not video_url:
            raise HTTPException(status_code=404, detail="Failed to fetch video URL")

        logger.info(f"Video URL fetched successfully: {video_url}")
        return {"video_url": video_url}

    except yt_dlp.utils.ExtractorError as e:
        logger.error(f"yt-dlp ExtractorError: {str(e)}")
        raise HTTPException(status_code=500, detail=f"yt-dlp extractor error: {str(e)}")

    except yt_dlp.DownloadError as e:
        logger.error(f"yt-dlp DownloadError: {str(e)}")
        raise HTTPException(status_code=500, detail=f"yt-dlp download error: {str(e)}")

    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
