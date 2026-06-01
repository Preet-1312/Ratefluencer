from fastapi import APIRouter
from pydantic import BaseModel
from services.script_service import generate_script
from services.news_service import get_news_trends
from services.youtube_service import get_youtube_trends
from services.trend_ranker import rank_trends

router = APIRouter(prefix="/scripts", tags=["scripts"])

class ScriptRequest(BaseModel):
    topic: str
    trend_score: int = 50
    duration: int = 60

@router.post("/generate")
def generate(req: ScriptRequest):
    script = generate_script(req.topic, req.trend_score, req.duration)
    return script

@router.get("/auto")
def auto_script():
    raw = []
    try:
        raw += get_news_trends()
    except:
        pass
    try:
        raw += get_youtube_trends()
    except:
        pass

    if not raw:
        return {"error": "No trends fetched. Check API keys."}

    ranked = rank_trends(raw)
    top = ranked[0]

    script = generate_script(
        topic=top["title"],
        trend_score=top["trend_score"],
        duration=60
    )
    script["source_trend"] = top
    return script