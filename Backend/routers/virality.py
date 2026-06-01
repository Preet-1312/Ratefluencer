from fastapi import APIRouter
from pydantic import BaseModel
from services.virality_service import predict_virality

router = APIRouter(prefix="/virality", tags=["virality"])

class ViralityRequest(BaseModel):
    topic: str
    hook: str = ""
    story: str = ""
    key_insights: list = []
    cta: str = ""
    word_count: int = 0
    trend_score: int = 50
    linkedin_hashtags: list = []
    instagram_hashtags: list = []

@router.post("/predict")
def predict(req: ViralityRequest):
    script = {
        "hook": req.hook,
        "story": req.story,
        "key_insights": req.key_insights,
        "cta": req.cta,
        "word_count": req.word_count,
        "trend_score": req.trend_score
    }
    linkedin = {"hashtags": req.linkedin_hashtags}
    instagram = {"hashtags": req.instagram_hashtags}
    return predict_virality(req.topic, script, linkedin, instagram)