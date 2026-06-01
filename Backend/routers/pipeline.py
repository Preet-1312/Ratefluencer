from fastapi import APIRouter
from pydantic import BaseModel
from services.news_service import get_news_trends
from services.youtube_service import get_youtube_trends
from services.trend_ranker import rank_trends
from services.script_service import generate_script
from services.content_service import generate_linkedin_post, generate_instagram_caption
from services.virality_service import predict_virality
from services.voiceover_service import generate_voiceover
from services.thumbnail_service import generate_thumbnail
from services.reel_service import (
    generate_broll_scenes,
    generate_subtitles,
    generate_srt,
    generate_reel_video
)

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


class PipelineRequest(BaseModel):
    topic: str = ""
    auto_trend: bool = True
    duration: int = 60


@router.post("/run")
def run_pipeline(req: PipelineRequest):
    result = {}

    # Step 1 — Trends
    raw = []
    try:
        raw += get_news_trends()
    except Exception as e:
        print(f"News error: {e}")
    try:
        raw += get_youtube_trends()
    except Exception as e:
        print(f"YouTube error: {e}")

    trends = rank_trends(raw) if raw else []
    result["trends"] = trends[:5]

    # Step 2 — Pick topic
    topic = req.topic
    trend_score = 75
    if req.auto_trend and trends:
        topic = topic or trends[0]["title"]
        trend_score = trends[0]["trend_score"]
    result["topic"] = topic

    # Step 3 — Script
    script = {}
    try:
        script = generate_script(topic, trend_score, req.duration)
    except Exception as e:
        print(f"Script error: {e}")
        script = {
            "hook": topic,
            "story": "",
            "key_insights": [],
            "cta": "Follow for more",
            "full_script": topic,
            "word_count": len(topic.split()),
            "estimated_duration_sec": 30,
            "topic": topic,
            "trend_score": trend_score
        }
    result["script"] = script

    # Step 4 — LinkedIn + Instagram
    linkedin = {}
    instagram = {}
    try:
        linkedin = generate_linkedin_post(topic, script)
    except Exception as e:
        print(f"LinkedIn error: {e}")
    try:
        instagram = generate_instagram_caption(topic, script)
    except Exception as e:
        print(f"Instagram error: {e}")
    result["linkedin"] = linkedin
    result["instagram"] = instagram

    # Step 5 — Virality
    virality = {}
    try:
        virality = predict_virality(
            topic,
            script,
            linkedin={"hashtags": linkedin.get("hashtags", [])},
            instagram={"hashtags": instagram.get("hashtags", [])}
        )
    except Exception as e:
        print(f"Virality error: {e}")
    result["virality"] = virality

    # Step 6 — Voiceover
    voiceover = {}
    try:
        voiceover = generate_voiceover(script.get("full_script", topic))
    except Exception as e:
        print(f"Voiceover error: {e}")
    result["voiceover"] = voiceover

    # Step 7 — Thumbnail
    thumbnail = {}
    try:
        thumbnail = generate_thumbnail(topic, script.get("hook", ""))
    except Exception as e:
        print(f"Thumbnail error: {e}")
    result["thumbnail"] = thumbnail

    # Step 8 — B-Roll scenes
    broll = []
    try:
        broll = generate_broll_scenes(script)
    except Exception as e:
        print(f"B-Roll error: {e}")
    result["broll"] = broll

    # Step 9 — Subtitles
    subtitles = []
    srt = ""
    try:
        full_script = script.get("full_script", topic)
        duration_sec = script.get("estimated_duration_sec", req.duration)
        subtitles = generate_subtitles(full_script, duration_sec)
        srt = generate_srt(subtitles)
    except Exception as e:
        print(f"Subtitles error: {e}")
    result["subtitles"] = subtitles
    result["srt"] = srt

    # Step 10 — Video assembly
    video = {}
    try:
        if broll and voiceover.get("audio_base64"):
            video = generate_reel_video(
                broll,
                voiceover["audio_base64"],
                subtitles
            )
        else:
            video = {
                "video_base64": None,
                "error": "Missing broll or voiceover for video assembly"
            }
    except Exception as e:
        print(f"Video error: {e}")
        video = {"video_base64": None, "error": str(e)}
    result["video"] = video

    # Summary
    result["summary"] = {
        "topic": topic,
        "trend_score": trend_score,
        "virality_score": virality.get("virality_score", 0),
        "word_count": script.get("word_count", 0),
        "duration_sec": script.get("estimated_duration_sec", 0),
        "linkedin_hashtags": len(linkedin.get("hashtags", [])),
        "instagram_hashtags": len(instagram.get("hashtags", [])),
        "voiceover_ready": bool(voiceover.get("audio_base64")),
        "thumbnail_ready": bool(thumbnail.get("image_base64")),
        "broll_scenes": len(broll),
        "subtitle_lines": len(subtitles),
        "video_ready": bool(video.get("video_base64")),
    }

    return result


@router.get("/demo")
def demo_cache():
    import json, os
    cache_path = os.path.join(os.path.dirname(__file__), "..", "demo_cache.json")
    try:
        with open(cache_path) as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"No cache found. Run /pipeline/run first. ({e})"}