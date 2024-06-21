from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
import os

from app.routers import subscriptions_router, channel_videos_router, video_details_router
from app.auth import auth_router
from app.dependencies import SECRET_KEY

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.include_router(auth_router)
app.include_router(subscriptions_router)
app.include_router(channel_videos_router)
app.include_router(video_details_router)
