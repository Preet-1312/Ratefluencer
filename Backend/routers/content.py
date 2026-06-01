from fastapi import APIRouter
from pydantic import BaseModel
from services.content_service import generate_linkedin_post, generate_instagram_caption

router = APIRouter(prefix="/content", tags=["content"])

class ContentRequest(BaseModel):
    topic: str
    hook: str = ""
    key_insights: list = []

@router.post("/linkedin")
def linkedin(req: ContentRequest):
    script = {"hook": req.hook, "key_insights": req.key_insights}
    return generate_linkedin_post(req.topic, script)

@router.post("/instagram")
def instagram(req: ContentRequest):
    script = {"hook": req.hook, "key_insights": req.key_insights}
    return generate_instagram_caption(req.topic, script)

@router.post("/both")
def both(req: ContentRequest):
    script = {"hook": req.hook, "key_insights": req.key_insights}
    return {
        "linkedin": generate_linkedin_post(req.topic, script),
        "instagram": generate_instagram_caption(req.topic, script)
    }