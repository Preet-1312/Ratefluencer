import io
import json
import base64
import zipfile
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from db import get_db
from models import ContentHistory

router = APIRouter(prefix="/pipeline", tags=["export"])

@router.get("/export/{task_id}")
def export_content_pack(task_id: str, db: Session = Depends(get_db)):
    record = db.query(ContentHistory).filter(ContentHistory.task_id == task_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if record.status != "completed":
        raise HTTPException(status_code=400, detail=f"Task status is {record.status}, cannot export yet.")
        
    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        
        # 1. Script
        if record.script:
            script_data = json.dumps(record.script, indent=2)
            zip_file.writestr("script.json", script_data)
            
            # Simple text script
            txt_script = (
                f"Topic: {record.topic}\n\n"
                f"Hook:\n{record.script.get('hook', '')}\n\n"
                f"Story:\n{record.script.get('story', '')}\n\n"
                f"Key Insights:\n" + "\n".join(f"- {x}" for x in record.script.get('key_insights', [])) + "\n\n"
                f"CTA:\n{record.script.get('cta', '')}\n\n"
                f"Full Script:\n{record.script.get('full_script', '')}\n"
            )
            zip_file.writestr("script.txt", txt_script)

        # 2. Captions
        captions_txt = ""
        if record.linkedin:
            captions_txt += f"=== LINKEDIN POST ===\n{record.linkedin.get('post_text', '')}\n\nHashtags: {', '.join(record.linkedin.get('hashtags', []))}\n\n"
        if record.instagram:
            captions_txt += f"=== INSTAGRAM CAPTION ===\n{record.instagram.get('caption_text', '')}\n\nHashtags: {', '.join(record.instagram.get('hashtags', []))}\n"
        if captions_txt:
            zip_file.writestr("captions.txt", captions_txt)

        # 3. SRT Subtitles
        if record.srt:
            zip_file.writestr("subtitles.srt", record.srt)
        elif record.subtitles:
            # Recreate SRT just in case
            from services.reel_service import generate_srt
            srt_data = generate_srt(record.subtitles)
            zip_file.writestr("subtitles.srt", srt_data)

        # 4. Voiceover Audio
        if record.voiceover and record.voiceover.get("audio_base64"):
            try:
                audio_bytes = base64.b64decode(record.voiceover["audio_base64"])
                zip_file.writestr("voiceover.mp3", audio_bytes)
            except Exception as e:
                print(f"Error packing audio: {e}")

        # 5. Thumbnail Image
        if record.thumbnail and record.thumbnail.get("image_base64"):
            try:
                image_bytes = base64.b64decode(record.thumbnail["image_base64"])
                zip_file.writestr("thumbnail.jpg", image_bytes)
            except Exception as e:
                print(f"Error packing thumbnail: {e}")

        # 6. Generated Video
        if record.video and record.video.get("video_base64"):
            try:
                video_bytes = base64.b64decode(record.video["video_base64"])
                zip_file.writestr("video.mp4", video_bytes)
            except Exception as e:
                print(f"Error packing video: {e}")

        # 7. Summary Readme
        summary_md = (
            f"# Content Pack: {record.topic}\n\n"
            f"- Generated on: {record.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"- Virality Score: {record.virality_score}/100\n"
            f"- Topic Score: {record.trend_score}/100\n\n"
            f"Thank you for using Viral Reel Agent! 🚀\n"
        )
        zip_file.writestr("README.md", summary_md)
        
    zip_buffer.seek(0)
    
    filename = f"content_pack_{task_id[:8]}.zip"
    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
