# app/routers/__init__.py
from .subscriptions import router as subscriptions_router
from .channel_videos import router as channel_videos_router
from .video_details import router as video_details_router

# 모든 라우터를 모아서 제공
__all__ = [
    "subscriptions_router",
    "channel_videos_router",
    "video_details_router",
]
