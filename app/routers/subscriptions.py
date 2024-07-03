from fastapi import APIRouter, Request, Header
from fastapi.responses import RedirectResponse
import httpx

from app.utils.token import load_credentials, save_credentials

router = APIRouter()

@router.get("/subscriptions")
async def subscriptions(userToken: str = Header(None, alias="x-token")):

    print(f'token: {userToken}')
    credentials = load_credentials(filepath=userToken)
    if not credentials or (credentials and credentials.expired and not credentials.refresh_token):
        return RedirectResponse(url="/auth")

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(httpx.AsyncClient())
        save_credentials(credentials)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/youtube/v3/subscriptions",
            params={
                "part": "snippet",
                "mine": "true"
            },
            headers={
                "Authorization": f"Bearer {credentials.token}"
            }
        )
    subscriptions_data = response.json()
    return subscriptions_data
