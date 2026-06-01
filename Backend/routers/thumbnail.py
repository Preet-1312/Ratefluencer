from fastapi import APIRouter
from pydantic import BaseModel
from services.thumbnail_service import generate_thumbnail

router = APIRouter(prefix="/thumbnail", tags=["thumbnail"])

class ThumbnailRequest(BaseModel):
    topic: str
    hook: str = ""

@router.post("/generate")
def generate(req: ThumbnailRequest):
    return generate_thumbnail(req.topic, req.hook)