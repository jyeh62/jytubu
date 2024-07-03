from fastapi import APIRouter, Request, Header, Query
from fastapi.responses import RedirectResponse
import httpx
from typing import List, Optional

from app.utils.token import load_credentials, save_credentials

router = APIRouter()

@router.get("/channel_videos/{channel_id}")
async def channel_videos(channel_id: str, 
                        page_token: Optional[str] = Query(None, alias="next_page_token"),
                        max_results: int = Query(50, ge=1, le=50),
                        userToken: str = Header(None, alias="x-token")):
    credentials = load_credentials(filepath=userToken)
    if not credentials or (credentials and credentials.expired and not credentials.refresh_token):
        return RedirectResponse(url="/auth")

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(httpx.AsyncClient())
        save_credentials(credentials)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={
                "part": "contentDetails",
                "id": channel_id,
            },
            headers={
                "Authorization": f"Bearer {credentials.token}"
            }
        )
        channels_data = response.json()
        uploads_playlist_id = channels_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        print(f"next: {page_token}, maxResult: {max_results}")
        response = await client.get(
            "https://www.googleapis.com/youtube/v3/playlistItems",
            params={
                "part": "snippet",
                "playlistId": uploads_playlist_id,
                "maxResults": max_results,
                "pageToken" :page_token
                
            },
            headers={
                "Authorization": f"Bearer {credentials.token}"
            }
        )
    videos_data = response.json()
    return videos_data
