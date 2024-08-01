from fastapi import APIRouter, Query, BackgroundTasks, HTTPException
from typing import Optional
import asyncio
import uuid
import yt_dlp
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

router = APIRouter()

download_tasks = {}


@router.get("/download/")
async def download(background_tasks: BackgroundTasks, url: Optional[str] = Query(None, alias="url")):
    print(url)
    options = {}
    task_id = str(uuid.uuid4())
    download_tasks[task_id] = {"status": "pending", "url": url}
    background_tasks.add_task(download_video, task_id, url, options)

    return {"task_id": task_id}


def download_with_yt_dlp(task_id: str, url, options):
    download_tasks[task_id]['status'] = 'in progress'
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])
    download_tasks[task_id]['status'] = 'completed'


async def download_video(task_id: str, url, options):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, download_with_yt_dlp, task_id, url, options)


@router.get("/download/{task_id}")
async def get_download_status(task_id: str):
    if task_id not in download_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return download_tasks[task_id]