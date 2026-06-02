"""
youtube_clips_service.py
Fetches real YouTube video clips related to a topic using the YouTube Data API v3.
Scores by relevance, suggests clip timestamps, and caches results for 2 hours.
"""
import os
import time
import re
from googleapiclient.discovery import build

# ─── In-memory cache: { "topic_lower": {"data": [...], "ts": float} }
_cache: dict = {}
_CACHE_TTL_SEC = 7200  # 2 hours


def _get_youtube():
    return build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))


# ─────────────────────────────────────────────
#  Duration string ISO 8601 → total seconds
# ─────────────────────────────────────────────
def _iso_duration_to_seconds(iso: str) -> int:
    match = re.match(
        r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or ""
    )
    if not match:
        return 0
    h = int(match.group(1) or 0)
    m = int(match.group(2) or 0)
    s = int(match.group(3) or 0)
    return h * 3600 + m * 60 + s


def _fmt_duration(seconds: int) -> str:
    if seconds < 60:
        return f"0:{seconds:02d}"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


# ─────────────────────────────────────────────
#  Relevance scoring  (0-100)
# ─────────────────────────────────────────────
def score_clip_relevance(clip: dict, topic: str) -> int:
    topic_words = set(re.sub(r"[^\w\s]", "", topic.lower()).split())
    title_words = set(re.sub(r"[^\w\s]", "", clip.get("title", "").lower()).split())

    # 1. Title keyword match – 40 pts
    if topic_words:
        overlap = len(topic_words & title_words) / len(topic_words)
        title_score = min(int(overlap * 40), 40)
    else:
        title_score = 0

    # 2. View count – 30 pts  (log-normalised, 1M views ≈ full 30 pts)
    views = clip.get("view_count", 0)
    if views > 0:
        import math
        view_score = min(int((math.log10(views + 1) / 6) * 30), 30)
    else:
        view_score = 0

    # 3. License bonus – 15 pts
    license_score = 15 if clip.get("license") == "creativeCommon" else 0

    # 4. Recency – 15 pts  (within the last year)
    published = clip.get("published_at", "")
    recency_score = 0
    if published:
        try:
            pub_year = int(published[:4])
            current_year = time.gmtime().tm_year
            if current_year - pub_year == 0:
                recency_score = 15
            elif current_year - pub_year == 1:
                recency_score = 10
            elif current_year - pub_year == 2:
                recency_score = 5
        except Exception:
            pass

    return title_score + view_score + license_score + recency_score


# ─────────────────────────────────────────────
#  Timestamp suggester
# ─────────────────────────────────────────────
def get_clip_timestamps(video_id: str, duration_sec: int) -> list:
    """Suggest 3 good clip windows (each 5-10 s) inside the video."""
    if duration_sec < 15:
        return [{"start": 0, "end": min(10, duration_sec), "reason": "Full short video"}]

    # Avoid first/last 15 % (intros/outros)
    usable_start = max(int(duration_sec * 0.15), 5)
    usable_end = int(duration_sec * 0.85)
    usable = usable_end - usable_start

    suggestions = []
    if usable >= 30:
        # Early middle
        s1 = usable_start
        suggestions.append({"start": s1, "end": s1 + 8, "reason": "Early main content section"})
        # True centre
        s2 = usable_start + usable // 2 - 4
        suggestions.append({"start": s2, "end": s2 + 8, "reason": "Core content highlight"})
        # Late middle
        s3 = usable_end - 10
        suggestions.append({"start": s3, "end": s3 + 8, "reason": "Late content / recap section"})
    else:
        s1 = usable_start
        suggestions.append({"start": s1, "end": min(s1 + 8, usable_end), "reason": "Main content section"})

    return suggestions


# ─────────────────────────────────────────────
#  Core search
# ─────────────────────────────────────────────
def search_youtube_clips(topic: str, max_results: int = 8) -> list:
    cache_key = topic.lower().strip()
    now = time.time()

    # Check cache
    if cache_key in _cache:
        entry = _cache[cache_key]
        if now - entry["ts"] < _CACHE_TTL_SEC:
            return entry["data"][:max_results]

    try:
        youtube = _get_youtube()

        # ── Search request (100 units) ──
        search_resp = youtube.search().list(
            q=topic,
            part="id,snippet",
            type="video",
            videoDuration="short",          # under 4 minutes
            videoLicense="creativeCommon",  # CC-BY licensed
            order="relevance",
            maxResults=max_results,
            safeSearch="none",
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]

        if not video_ids:
            # Fallback: broader search (first 2 words, no license filter)
            broad_query = " ".join(topic.split()[:2])
            search_resp = youtube.search().list(
                q=broad_query,
                part="id,snippet",
                type="video",
                videoDuration="short",
                order="viewCount",
                maxResults=max_results,
            ).execute()
            video_ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]

        if not video_ids:
            return []

        # ── Video details (1 unit per video) ──
        details_resp = youtube.videos().list(
            part="snippet,statistics,contentDetails,status",
            id=",".join(video_ids),
        ).execute()

        clips = []
        for item in details_resp.get("items", []):
            vid_id = item["id"]
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})
            status = item.get("status", {})

            duration_sec = _iso_duration_to_seconds(content.get("duration", ""))
            view_count = int(stats.get("viewCount", 0))

            # Best available thumbnail
            thumbs = snippet.get("thumbnails", {})
            thumb_url = (
                thumbs.get("maxres", {}).get("url")
                or thumbs.get("high", {}).get("url")
                or thumbs.get("default", {}).get("url")
                or f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg"
            )

            license_type = status.get("license", "youtube")

            clip = {
                "video_id": vid_id,
                "title": snippet.get("title", ""),
                "channel_name": snippet.get("channelTitle", ""),
                "view_count": view_count,
                "view_count_formatted": _fmt_views(view_count),
                "duration_sec": duration_sec,
                "duration": _fmt_duration(duration_sec),
                "thumbnail_url": thumb_url,
                "youtube_url": f"https://www.youtube.com/watch?v={vid_id}",
                "embed_url": f"https://www.youtube.com/embed/{vid_id}",
                "license": license_type,
                "is_creative_commons": license_type == "creativeCommon",
                "published_at": snippet.get("publishedAt", ""),
                "timestamps": get_clip_timestamps(vid_id, duration_sec),
                "relevance_score": 0,  # filled below
            }
            clip["relevance_score"] = score_clip_relevance(clip, topic)
            clips.append(clip)

        # Sort by relevance score descending
        clips.sort(key=lambda c: c["relevance_score"], reverse=True)

        # Store in cache
        _cache[cache_key] = {"data": clips, "ts": now}
        return clips[:max_results]

    except Exception as e:
        print(f"[youtube_clips_service] search error: {e}")
        return []


def _fmt_views(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M views"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K views"
    return f"{n} views"


# ─────────────────────────────────────────────
#  Top-N best clips
# ─────────────────────────────────────────────
def get_best_clips(topic: str, count: int = 3) -> list:
    all_clips = search_youtube_clips(topic, max_results=8)
    return all_clips[:count]
