from fastapi import APIRouter, Query
from typing import Optional
import uuid
import yt_dlp

router = APIRouter()

@router.get("/download/")
async def download(url: Optional[str] = Query(None, alias="url"),):
    print(url)
    random_uuid = uuid.uuid4()
    print(random_uuid)
    options = {}
    with yt_dlp.YoutubeDL(options) as ydl:
        await ydl.download([url])

    return {"uuid": random_uuid}
