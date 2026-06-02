import os
import base64
import tempfile
import requests
from urllib.parse import quote

# Patch for Pillow 10+ compatibility with MoviePy
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS


def generate_broll_scenes(script: dict) -> list:
    scenes = []
    insights = script.get("key_insights", [])
    hook = script.get("hook", "")

    prompts = [
        f"Cinematic abstract visualization: {hook[:80]}, dark moody atmosphere, 4K cinematic",
    ]
    for insight in insights[:3]:
        prompts.append(
            f"Professional cinematic scene: {insight[:80]}, dark background, dramatic lighting, no text"
        )

    for i, prompt in enumerate(prompts):
        encoded = quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true&seed={i*42}"
        
        # Try up to 3 times
        for attempt in range(3):
            try:
                res = requests.get(url, timeout=45)
                if res.status_code == 200:
                    b64 = base64.b64encode(res.content).decode("utf-8")
                    scenes.append({
                        "scene": i + 1,
                        "prompt": prompt[:80],
                        "image_base64": b64,
                        "duration_sec": 5 if i == 0 else 8
                    })
                    break
            except Exception as e:
                print(f"B-roll scene {i} attempt {attempt+1} failed: {e}")
                if attempt == 2:
                    print(f"Skipping scene {i+1} after 3 attempts")

    return scenes


def generate_subtitles(full_script: str, duration_sec: int) -> list:
    words = full_script.split()
    if not words:
        return []

    words_per_sec = len(words) / max(duration_sec, 1)
    chunk_size = max(int(words_per_sec * 3), 4)

    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    subtitles = []
    time_per_chunk = duration_sec / max(len(chunks), 1)

    for i, chunk in enumerate(chunks):
        start = i * time_per_chunk
        end = (i + 1) * time_per_chunk
        subtitles.append({
            "index": i + 1,
            "start": round(start, 2),
            "end": round(end, 2),
            "start_fmt": _fmt_time(start),
            "end_fmt": _fmt_time(end),
            "text": chunk
        })

    return subtitles


def generate_srt(subtitles: list) -> str:
    srt = ""
    for s in subtitles:
        srt += f"{s['index']}\n"
        srt += f"{s['start_fmt']} --> {s['end_fmt']}\n"
        srt += f"{s['text']}\n\n"
    return srt


def _fmt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_reel_video(broll_scenes: list, voiceover_b64: str, subtitles: list) -> dict:
    try:
        from moviepy.editor import (
            ImageClip,
            AudioFileClip,
            concatenate_videoclips
        )

        clips = []
        temp_files = []

        for scene in broll_scenes:
            try:
                img_bytes = base64.b64decode(scene["image_base64"])
                tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                tmp_img.write(img_bytes)
                tmp_img.close()
                temp_files.append(tmp_img.name)

                duration = scene.get("duration_sec", 5)
                clip = ImageClip(tmp_img.name).set_duration(duration)
                clip = clip.resize(height=720)
                clips.append(clip)
            except Exception as e:
                print(f"Clip error scene {scene.get('scene')}: {e}")

        if not clips:
            return {"video_base64": None, "error": "No valid b-roll clips"}

        video = concatenate_videoclips(clips, method="compose")

        audio_bytes = base64.b64decode(voiceover_b64)
        tmp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp_audio.write(audio_bytes)
        tmp_audio.close()
        temp_files.append(tmp_audio.name)

        audio = AudioFileClip(tmp_audio.name)
        final_duration = min(video.duration, audio.duration)
        video = video.set_audio(audio).set_duration(final_duration)

        tmp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp_video.close()
        temp_files.append(tmp_video.name)

        tmp_audio_render = tmp_video.name + "_temp.m4a"

        video.write_videofile(
            tmp_video.name,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            logger=None,
            temp_audiofile=tmp_audio_render
        )

        with open(tmp_video.name, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode("utf-8")

        for fp in temp_files:
            try:
                os.unlink(fp)
            except:
                pass
        try:
            os.unlink(tmp_audio_render)
        except:
            pass

        return {
            "video_base64": video_b64,
            "format": "mp4",
            "duration_sec": round(final_duration),
            "scenes_used": len(clips)
        }

    except ImportError:
        return {
            "video_base64": None,
            "error": "moviepy not installed. Run: pip install moviepy==1.0.3"
        }
    except Exception as e:
        return {
            "video_base64": None,
            "error": str(e)
        }