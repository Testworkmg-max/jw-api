from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="JW.org Video API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

JW_API = "https://b.jw-cdn.org/apis/mediator/v1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.jw.org/",
}

@app.get("/api/videos")
def get_videos(
    lang: str = Query("MG"),
    category: str = Query("VODTeenagers"),
):
    try:
        url = f"{JW_API}/categories/{lang}/{category}?detailed=1&clientType=www"
        resp = requests.get(url, timeout=30, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()

        media_list = data.get("category", {}).get("media", [])
        cat_name = data.get("category", {}).get("name", "")

        videos = []
        for media in media_list:
            title = media.get("title", "Sans titre")
            duration = int(media.get("duration", 0))
            guid = media.get("guid", "")
            docid = media.get("docid", "")

            files = media.get("files", [])
            download_url = ""
            for f in files:
                if "progressiveDownloadURL" in f:
                    download_url = f["progressiveDownloadURL"]

            watch_url = f"https://www.jw.org/finder?wtlocale={lang}&docid={docid}"

            videos.append({
                "id": guid or docid,
                "title": title,
                "duration": duration,
                "download_url": download_url,
                "watch_url": watch_url,
                "over_30s": duration > 30,
            })

        return {
            "category_name": cat_name,
            "total": len(videos),
            "over_30s_count": sum(1 for v in videos if v["over_30s"]),
            "videos": videos,
        }

    except Exception as e:
        return {
            "error": str(e),
            "category_name": "",
            "total": 0,
            "over_30s_count": 0,
            "videos": [],
        }

@app.get("/")
def root():
    return {"status": "ok", "message": "JW.org Video API"}
