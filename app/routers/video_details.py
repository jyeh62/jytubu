from fastapi import APIRouter, Request, Header
from fastapi.responses import RedirectResponse
import httpx

from app.utils.token import load_credentials, save_credentials

router = APIRouter()

@router.get("/video_details/{video_id}")
async def video_details(video_id: str, userToken: str = Header(None, alias="x-token")):
    credentials = load_credentials(userToken)
    if not credentials or (credentials and credentials.expired and not credentials.refresh_token):
        return RedirectResponse(url="/auth")

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(httpx.AsyncClient())
        save_credentials(credentials)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet,contentDetails,statistics,player",
                "id": video_id
            },
            headers={
                "Authorization": f"Bearer {credentials.token}"
            }
        )
    video_data = response.json()
    return video_data

