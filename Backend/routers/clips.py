"""
routers/clips.py
YouTube Clip Fetcher endpoints.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services.youtube_clips_service import (
    search_youtube_clips,
    get_best_clips,
    get_clip_timestamps,
)

router = APIRouter(prefix="/clips", tags=["clips"])


# ── Request Schemas ────────────────────────────────────────────────────────────
class ClipSearchRequest(BaseModel):
    topic: str
    max_results: Optional[int] = 8


class BestClipsRequest(BaseModel):
    topic: str
    count: Optional[int] = 3


# ── POST /clips/search ─────────────────────────────────────────────────────────
@router.post("/search")
def search_clips(req: ClipSearchRequest):
    clips = search_youtube_clips(req.topic, max_results=req.max_results)
    cc_count = sum(1 for c in clips if c.get("is_creative_commons"))
    return {
        "clips": clips,
        "total": len(clips),
        "creative_commons_count": cc_count,
        "topic": req.topic,
    }


# ── POST /clips/best ───────────────────────────────────────────────────────────
@router.post("/best")
def best_clips(req: BestClipsRequest):
    clips = get_best_clips(req.topic, count=req.count)
    cc_count = sum(1 for c in clips if c.get("is_creative_commons"))
    return {
        "clips": clips,
        "total": len(clips),
        "creative_commons_count": cc_count,
        "topic": req.topic,
    }


# ── GET /clips/embed/{video_id} ────────────────────────────────────────────────
@router.get("/embed/{video_id}")
def get_embed(video_id: str, duration: Optional[int] = 120):
    timestamps = get_clip_timestamps(video_id, duration)
    best = timestamps[0] if timestamps else {"start": 0, "end": 10}
    return {
        "video_id": video_id,
        "embed_url": f"https://www.youtube.com/embed/{video_id}",
        "embed_url_with_start": f"https://www.youtube.com/embed/{video_id}?start={best['start']}&end={best['end']}&autoplay=1",
        "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
        "suggested_timestamps": timestamps,
        "best_timestamp": best,
    }
