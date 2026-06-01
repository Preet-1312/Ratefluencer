from fastapi import APIRouter
from pydantic import BaseModel
from services.voiceover_service import generate_voiceover

router = APIRouter(prefix="/voiceover", tags=["voiceover"])

class VoiceoverRequest(BaseModel):
    script: str

@router.post("/generate")
def generate(req: VoiceoverRequest):
    return generate_voiceover(req.script)