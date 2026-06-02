import uuid
import asyncio
import os
import json
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db, SessionLocal
from models import ContentHistory, BrandVoice
from services.websocket_manager import ws_manager

# Services
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
# ML Upgrades
from services.ml_engagement_model import (
    predict_engagement,
    analyze_saturation,
    classify_category,
    classify_velocity,
    predict_posting_time
)
# YouTube Clips
from services.youtube_clips_service import get_best_clips

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

class PipelineRequest(BaseModel):
    topic: str = ""
    auto_trend: bool = True
    duration: int = 60
    brand_voice_id: int = None

# Async task runner
def run_pipeline_task(task_id: str, topic: str, auto_trend: bool, duration: int, brand_voice_id: int = None):
    # Standard DB session for background task
    db = SessionLocal()
    
    # Simple helper to send status updates
    async def update_status(progress: int, current_step: str, status: str = "processing", message: str = "", extra_data: dict = None):
        # Update database
        record = db.query(ContentHistory).filter(ContentHistory.task_id == task_id).first()
        if record:
            record.progress = progress
            record.current_step = current_step
            record.status = status
            if extra_data:
                for key, val in extra_data.items():
                    setattr(record, key, val)
            db.commit()
            
        # Broadcast via WebSockets
        ws_payload = {
            "task_id": task_id,
            "status": status,
            "progress": progress,
            "step": current_step,
            "message": message
        }
        if extra_data and "summary" in extra_data:
            ws_payload["summary"] = extra_data["summary"]
            
        await ws_manager.broadcast(task_id, ws_payload)

    # Wrap the sync pipeline run inside async workflow loop
    async def execute():
        try:
            results = {}
            
            # Retrieve active Brand Voice if provided
            brand_voice_style = None
            if brand_voice_id:
                voice = db.query(BrandVoice).filter(BrandVoice.id == brand_voice_id).first()
                if voice:
                    brand_voice_style = f"Tone: {voice.tone}. Style Guide: {voice.style_guide}"

            # Step 1 — Trends
            await update_status(10, "trends", message="Fetching latest trends from News and YouTube...")
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
            results["trends"] = trends[:10]

            # Step 2 — Pick topic
            await update_status(20, "topic", message="Analyzing and selecting optimal trend topic...")
            selected_topic = topic
            trend_score = 75
            velocity = "rising"
            
            if auto_trend and trends:
                selected_topic = selected_topic or trends[0]["title"]
                trend_score = trends[0]["trend_score"]
                velocity = classify_velocity(trends[0].get("score", 0), trends[0].get("comments", 0))
            results["topic"] = selected_topic

            # Step 3 — Script
            await update_status(35, "script", message="Generating structured video script (Hook, Story, CTA)...")
            script = {}
            try:
                script = generate_script(selected_topic, trend_score, duration, brand_voice_style)
            except Exception as e:
                print(f"Script error: {e}")
                script = {
                    "hook": selected_topic,
                    "story": "Story outline detailing this concept.",
                    "key_insights": [selected_topic[:50]],
                    "cta": "Follow for more daily insights!",
                    "full_script": selected_topic,
                    "word_count": len(selected_topic.split()),
                    "estimated_duration_sec": 30,
                    "topic": selected_topic,
                    "trend_score": trend_score
                }
            results["script"] = script

            # Step 4 — LinkedIn + Instagram posts
            await update_status(50, "captions", message="Generating tailored LinkedIn & Instagram captions...")
            linkedin = {}
            instagram = {}
            try:
                linkedin = generate_linkedin_post(selected_topic, script, brand_voice_style)
            except Exception as e:
                print(f"LinkedIn error: {e}")
            try:
                instagram = generate_instagram_caption(selected_topic, script, brand_voice_style)
            except Exception as e:
                print(f"Instagram error: {e}")
            results["linkedin"] = linkedin
            results["instagram"] = instagram

            # Step 5 — Virality & ML analysis
            await update_status(60, "virality", message="Calculating ML engagement metrics & saturation indexes...")
            virality = {}
            try:
                # 1. Base virality prediction using Groq
                base_virality = predict_virality(
                    selected_topic,
                    script,
                    linkedin={"hashtags": linkedin.get("hashtags", [])},
                    instagram={"hashtags": instagram.get("hashtags", [])}
                )
                
                # 2. Advanced ML predictions using scikit-learn models
                category = classify_category(selected_topic)
                ml_preds = predict_engagement(
                    trend_score=trend_score,
                    word_count=script.get("word_count", 80),
                    hook=script.get("hook", ""),
                    script_text=script.get("full_script", ""),
                    category_name=category
                )
                
                # 3. Saturation analysis
                saturation = analyze_saturation(selected_topic, db)
                
                # 4. Optimal posting times
                post_times = predict_posting_time(category, velocity)
                
                # Compile everything into a unified ML analytics response
                virality = {
                    "virality_score": ml_preds["virality_score"],
                    "confidence": base_virality.get("confidence", "high"),
                    "readability_score": ml_preds["readability"],
                    "sentiment_score": ml_preds["sentiment"],
                    "category": category,
                    "velocity_class": velocity,
                    "saturation": saturation,
                    "optimal_posting_times": post_times,
                    "instagram": ml_preds["instagram"],
                    "linkedin": ml_preds["linkedin"],
                    "strengths": base_virality.get("strengths", ["Clear hook", "Strong CTA"]),
                    "weaknesses": base_virality.get("weaknesses", ["Highly technical"]),
                    "improvement_tips": base_virality.get("improvement_tips", ["Add visuals"]),
                    "verdict": base_virality.get("verdict", "Good engagement potential.")
                }
            except Exception as e:
                print(f"Virality error: {e}")
                virality = {
                    "virality_score": 70,
                    "instagram": {"views": "10000-20000"},
                    "linkedin": {"views": "2000-5000"},
                    "readability_score": 60,
                    "sentiment_score": 0.2
                }
            results["virality"] = virality

            # Step 6 — Voiceover
            await update_status(70, "voiceover", message="Synthesizing high-fidelity voiceover track...")
            voiceover = {}
            try:
                voiceover = generate_voiceover(script.get("full_script", selected_topic))
            except Exception as e:
                print(f"Voiceover error: {e}")
            results["voiceover"] = voiceover

            # Step 7 — Thumbnail
            await update_status(80, "thumbnail", message="Generating eye-catching thumbnail visual...")
            thumbnail = {}
            try:
                thumbnail = generate_thumbnail(selected_topic, script.get("hook", ""))
            except Exception as e:
                print(f"Thumbnail error: {e}")
            results["thumbnail"] = thumbnail

            # Step 8 — B-Roll scenes
            await update_status(85, "broll", message="Generating scene image assets via Pollinations.ai...")
            broll = []
            try:
                broll = generate_broll_scenes(script)
            except Exception as e:
                print(f"B-Roll error: {e}")
            results["broll"] = broll

            # Step 8.5 — YouTube Reference Clips
            await update_status(87, "youtube_clips", message="Fetching real YouTube reference clips...")
            yt_clips = []
            try:
                yt_clips = get_best_clips(selected_topic, count=3)
            except Exception as e:
                print(f"YouTube clips error: {e}")
            results["youtube_clips"] = yt_clips

            # Step 9 — Subtitles
            await update_status(90, "subtitles", message="Formatting SRT timed subtitle captions...")
            subtitles = []
            srt = ""
            try:
                full_script = script.get("full_script", selected_topic)
                duration_sec = script.get("estimated_duration_sec", duration)
                subtitles = generate_subtitles(full_script, duration_sec)
                srt = generate_srt(subtitles)
            except Exception as e:
                print(f"Subtitles error: {e}")
            results["subtitles"] = subtitles
            results["srt"] = srt

            # Step 10 — Video Assembly
            await update_status(95, "video", message="Assembling final MP4 video with captions (MoviePy)...")
            video = {}
            try:
                if broll and voiceover.get("audio_base64"):
                    video = generate_reel_video(
                        broll,
                        voiceover["audio_base64"],
                        subtitles
                    )
                else:
                    video = {"video_base64": None, "error": "B-roll or voiceover missing"}
            except Exception as e:
                print(f"Video assembly error: {e}")
                video = {"video_base64": None, "error": str(e)}
            results["video"] = video

            # Build final pipeline summary
            summary = {
                "topic": selected_topic,
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
                "youtube_clips_found": len(yt_clips),
            }
            
            # Save all results to Database
            db_data = {
                "status": "completed",
                "progress": 100,
                "current_step": "complete",
                "trend_score": trend_score,
                "virality_score": virality.get("virality_score", 0),
                "script": script,
                "linkedin": linkedin,
                "instagram": instagram,
                "virality": virality,
                "voiceover": voiceover,
                "thumbnail": thumbnail,
                "broll": broll,
                "subtitles": subtitles,
                "srt": srt,
                "video": video,
                "youtube_clips": yt_clips
            }
            
            await update_status(100, "complete", status="completed", message="Pipeline finished successfully!", extra_data=db_data)
            
            # Save to demo cache for backward compatibility
            try:
                cache_path = os.path.join(os.path.dirname(__file__), "..", "demo_cache.json")
                with open(cache_path, "w") as f:
                    # Filter video base64 out of demo_cache to keep file size small
                    lightweight_results = {**results, "summary": summary}
                    if "video" in lightweight_results:
                        lightweight_results["video"] = {**lightweight_results["video"], "video_base64": None}
                    json.dump(lightweight_results, f)
            except Exception as cache_err:
                print(f"Error writing demo cache: {cache_err}")

        except Exception as pipeline_err:
            print(f"Pipeline crashed: {pipeline_err}")
            await update_status(100, "failed", status="failed", message=f"Pipeline failed: {str(pipeline_err)}")
        finally:
            db.close()

    # Schedule run in event loop
    asyncio.run(execute())


@router.post("/run")
def run_pipeline(req: PipelineRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task_id = str(uuid.uuid4())
    
    # Store initial record
    new_task = ContentHistory(
        task_id=task_id,
        topic=req.topic or "Auto Trending Topic",
        status="pending",
        progress=0,
        current_step="start"
    )
    db.add(new_task)
    db.commit()

    # Dispatch to background tasks
    background_tasks.add_task(
        run_pipeline_task,
        task_id,
        req.topic,
        req.auto_trend,
        req.duration,
        req.brand_voice_id
    )

    return {
        "task_id": task_id,
        "status": "pending",
        "progress": 0,
        "message": "Pipeline worker successfully dispatched."
    }


@router.get("/status/{task_id}")
def get_pipeline_status(task_id: str, db: Session = Depends(get_db)):
    record = db.query(ContentHistory).filter(ContentHistory.task_id == task_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Task not found")
        
    response = {
        "task_id": record.task_id,
        "topic": record.topic,
        "status": record.status,
        "progress": record.progress,
        "current_step": record.current_step,
        "created_at": record.created_at.isoformat()
    }
    
    if record.status == "completed":
        response["results"] = {
            "topic": record.topic,
            "script": record.script,
            "linkedin": record.linkedin,
            "instagram": record.instagram,
            "virality": record.virality,
            "voiceover": record.voiceover,
            "thumbnail": record.thumbnail,
            "broll": record.broll,
            "subtitles": record.subtitles,
            "srt": record.srt,
            "video": record.video,
            "youtube_clips": record.youtube_clips,
            "summary": {
                "topic": record.topic,
                "trend_score": record.trend_score,
                "virality_score": record.virality_score,
                "word_count": record.script.get("word_count", 0) if record.script else 0,
                "duration_sec": record.script.get("estimated_duration_sec", 0) if record.script else 0,
                "voiceover_ready": bool(record.voiceover.get("audio_base64")) if record.voiceover else False,
                "thumbnail_ready": bool(record.thumbnail.get("image_base64")) if record.thumbnail else False,
                "video_ready": bool(record.video.get("video_base64")) if record.video else False,
                "youtube_clips_found": len(record.youtube_clips) if record.youtube_clips else 0
            }
        }
    elif record.status == "failed":
        response["error"] = record.current_step
        
    return response


@router.get("/history")
def get_pipeline_history(db: Session = Depends(get_db)):
    records = db.query(ContentHistory).order_by(ContentHistory.created_at.desc()).all()
    history_list = []
    
    for r in records:
        history_list.append({
            "task_id": r.task_id,
            "topic": r.topic,
            "status": r.status,
            "progress": r.progress,
            "current_step": r.current_step,
            "trend_score": r.trend_score,
            "virality_score": r.virality_score,
            "created_at": r.created_at.isoformat(),
            "has_video": bool(r.video and r.video.get("video_base64")),
            "has_voiceover": bool(r.voiceover and r.voiceover.get("audio_base64")),
            "has_thumbnail": bool(r.thumbnail and r.thumbnail.get("image_base64")),
            "word_count": r.script.get("word_count", 0) if r.script else 0,
            "duration_sec": r.script.get("estimated_duration_sec", 0) if r.script else 0
        })
        
    return history_list


@router.get("/demo")
def demo_cache():
    # Attempt to fetch latest completed item from Database first
    db = SessionLocal()
    try:
        latest = db.query(ContentHistory).filter(ContentHistory.status == "completed").order_by(ContentHistory.created_at.desc()).first()
        if latest:
            return {
                "topic": latest.topic,
                "script": latest.script,
                "linkedin": latest.linkedin,
                "instagram": latest.instagram,
                "virality": latest.virality,
                "voiceover": latest.voiceover,
                "thumbnail": latest.thumbnail,
                "broll": latest.broll,
                "subtitles": latest.subtitles,
                "srt": latest.srt,
                "video": latest.video,
                "youtube_clips": latest.youtube_clips,
                "summary": {
                    "topic": latest.topic,
                    "trend_score": latest.trend_score,
                    "virality_score": latest.virality_score,
                    "word_count": latest.script.get("word_count", 0) if latest.script else 0,
                    "duration_sec": latest.script.get("estimated_duration_sec", 0) if latest.script else 0,
                    "voiceover_ready": bool(latest.voiceover.get("audio_base64")) if latest.voiceover else False,
                    "thumbnail_ready": bool(latest.thumbnail.get("image_base64")) if latest.thumbnail else False,
                    "video_ready": bool(latest.video.get("video_base64")) if latest.video else False,
                    "youtube_clips_found": len(latest.youtube_clips) if latest.youtube_clips else 0
                }
            }
    except Exception as e:
        print(f"Db demo check fail: {e}")
    finally:
        db.close()

    # Standard demo cache file fallback
    import os
    cache_path = os.path.join(os.path.dirname(__file__), "..", "demo_cache.json")
    try:
        with open(cache_path) as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"No cache found. Run /pipeline/run first. ({e})"}