from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from services.reel_service import (
    generate_broll_scenes,
    generate_subtitles,
    generate_srt,
    generate_reel_video
)

router = APIRouter(prefix="/reel", tags=["reel"])


class ReelRequest(BaseModel):
    script: dict
    duration_sec: int = 60


class VideoRequest(BaseModel):
    broll: list
    voiceover_b64: str
    subtitles: list = []


@router.post("/broll")
def broll(req: ReelRequest):
    scenes = generate_broll_scenes(req.script)
    return {"scenes": scenes, "total": len(scenes)}


@router.post("/subtitles")
def subtitles(req: ReelRequest):
    full_script = req.script.get("full_script", "")
    subs = generate_subtitles(full_script, req.duration_sec)
    srt = generate_srt(subs)
    return {
        "subtitles": subs,
        "srt_content": srt,
        "total_lines": len(subs)
    }


@router.post("/subtitles/download")
def download_srt(req: ReelRequest):
    full_script = req.script.get("full_script", "")
    subs = generate_subtitles(full_script, req.duration_sec)
    srt = generate_srt(subs)
    return PlainTextResponse(
        content=srt,
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=subtitles.srt"}
    )


@router.post("/video")
def create_video(req: VideoRequest):
    return generate_reel_video(req.broll, req.voiceover_b64, req.subtitles)