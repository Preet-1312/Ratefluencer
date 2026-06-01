from fastapi import APIRouter
from services.reddit_service import get_reddit_trends
from services.news_service import get_news_trends
from services.youtube_service import get_youtube_trends
from services.trend_ranker import rank_trends

router = APIRouter(prefix="/trends", tags=["trends"])

@router.get("/discover")
def discover_trends():
    raw = []
    try:
        raw += get_reddit_trends()
    except Exception as e:
        print(f"Reddit error: {e}")
    try:
        raw += get_news_trends()
    except Exception as e:
        print(f"News error: {e}")
    try:
        raw += get_youtube_trends()
    except Exception as e:
        print(f"YouTube error: {e}")

    ranked = rank_trends(raw)
    return {"trends": ranked[:10], "total_fetched": len(raw)}