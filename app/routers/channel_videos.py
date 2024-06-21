from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import httpx

from app.utils.token import load_credentials, save_credentials

router = APIRouter()

@router.get("/channel_videos/{channel_id}")
async def channel_videos(channel_id: str):
    credentials = load_credentials()
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
                "id": channel_id
            },
            headers={
                "Authorization": f"Bearer {credentials.token}"
            }
        )
        channels_data = response.json()
        uploads_playlist_id = channels_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        response = await client.get(
            "https://www.googleapis.com/youtube/v3/playlistItems",
            params={
                "part": "snippet",
                "playlistId": uploads_playlist_id,
                "maxResults": 10
            },
            headers={
                "Authorization": f"Bearer {credentials.token}"
            }
        )
    videos_data = response.json()
    return videos_data
