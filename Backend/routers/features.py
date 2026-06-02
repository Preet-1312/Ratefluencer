from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from db import get_db
from models import BrandVoice
from services.features_service import (
    analyze_competitors,
    generate_content_calendar,
    repurpose_content,
    generate_reel_series
)
from services.ml_engagement_model import calculate_readability, analyze_sentiment, predict_engagement
from services.script_service import generate_script
import os
import json
import re
from groq import Groq

router = APIRouter(prefix="/pipeline", tags=["features"])

# Pydantic Schemas
class BrandVoiceCreate(BaseModel):
    name: str
    tone: str
    style_guide: str
    hashtags: Optional[str] = ""

class BrandVoiceResponse(BaseModel):
    id: int
    name: str
    tone: str
    style_guide: str
    hashtags: str
    is_active: bool

    class Config:
        from_attributes = True

class CalendarRequest(BaseModel):
    topic: str
    brand_voice: Optional[str] = "Standard"

class RepurposingRequest(BaseModel):
    topic: str
    script: dict

class HookTestRequest(BaseModel):
    topic: str
    brand_voice: Optional[str] = "Standard"


# --- COMPETITOR ANALYSIS ---
@router.get("/competitors")
def get_competitor_analysis(topic: str):
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")
    return {"competitors": analyze_competitors(topic)}


# --- CONTENT CALENDAR ---
@router.post("/calendar")
def get_calendar(req: CalendarRequest):
    return {"calendar": generate_content_calendar(req.topic, req.brand_voice)}


# --- REPURPOSING ---
@router.post("/repurpose")
def get_repurposing(req: RepurposingRequest):
    return repurpose_content(req.topic, req.script)


# --- REEL SERIES ---
@router.get("/series")
def get_series(topic: str):
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")
    return {"series": generate_reel_series(topic)}


# --- HOOK A/B TESTING ---
@router.post("/ab-hooks")
def get_ab_hooks(req: HookTestRequest):
    # Call Groq to generate 3 hooks
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    prompt = f"""You are a viral hook copywriter. Generate 3 diverse hook variations for the topic: "{req.topic}".
    Brand Tone: {req.brand_voice}
    
    1. Curiosity Loop (makes them ask a question)
    2. Authority Callout (establishes trust/industry secrets)
    3. Contrary/Contrarian (goes against common wisdom)
    
    Return a valid JSON array of 3 objects. Return ONLY valid JSON, no markdown, no backticks.
    Format:
    [
      {{"type": "Curiosity Loop", "hook": "The hook sentence here"}},
      {{"type": "Authority Callout", "hook": "The hook sentence here"}},
      {{"type": "Contrarian", "hook": "The hook sentence here"}}
    ]"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.6
        )
        raw = response.choices[0].message.content.strip()
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            raw = match.group(0)
            
        raw = re.sub(r',\s*\]', ']', raw)
        raw = re.sub(r',\s*\}', '}', raw)
        
        hooks = json.loads(raw)
    except Exception as e:
        print(f"Hook generation error: {e}")
        hooks = [
            {"type": "Curiosity Loop", "hook": f"The hidden secret about {req.topic} no one tells you."},
            {"type": "Authority Callout", "hook": f"After analyzing 100 cases, this is the truth about {req.topic}."},
            {"type": "Contrarian", "hook": f"Stop trying to learn {req.topic} the old way. It's holding you back."}
        ]
        
    scored_hooks = []
    for h in hooks:
        hook_text = h.get("hook", "")
        # Score each hook
        readability = calculate_readability(hook_text)
        sentiment = analyze_sentiment(hook_text)
        
        # Predict engagement (simulate script length around 100 words for baseline)
        preds = predict_engagement(85, 100, hook_text, hook_text, "tech")
        
        scored_hooks.append({
            "type": h.get("type", "General"),
            "hook": hook_text,
            "readability": readability,
            "sentiment": sentiment,
            "predicted_virality": preds.get("virality_score", 50),
            "predicted_ig_views": preds.get("instagram", {}).get("views", "1000-5000"),
            "predicted_li_views": preds.get("linkedin", {}).get("views", "500-2000")
        })
        
    # Sort by predicted virality
    scored_hooks = sorted(scored_hooks, key=lambda x: x["predicted_virality"], reverse=True)
    return {"hooks": scored_hooks}


# --- BRAND VOICE CRUD ---
@router.post("/brand-voice", response_model=BrandVoiceResponse)
def create_brand_voice(voice: BrandVoiceCreate, db: Session = Depends(get_db)):
    # Deactivate other voices if needed or keep it simple
    db_voice = BrandVoice(
        name=voice.name,
        tone=voice.tone,
        style_guide=voice.style_guide,
        hashtags=voice.hashtags,
        is_active=True
    )
    
    # Set all other voices to inactive
    db.query(BrandVoice).update({BrandVoice.is_active: False})
    
    db.add(db_voice)
    db.commit()
    db.refresh(db_voice)
    return db_voice

@router.get("/brand-voice", response_model=List[BrandVoiceResponse])
def get_brand_voices(db: Session = Depends(get_db)):
    # If no voices exist, seed a standard one
    voices = db.query(BrandVoice).all()
    if not voices:
        default_voice = BrandVoice(
            name="Standard",
            tone="professional",
            style_guide="Clear, concise, educational, formatted with bullet points, conversational but expert tone.",
            hashtags="analytics,tech,growth",
            is_active=True
        )
        db.add(default_voice)
        db.commit()
        db.refresh(default_voice)
        voices = [default_voice]
    return voices

@router.post("/brand-voice/{id}/activate")
def activate_brand_voice(id: int, db: Session = Depends(get_db)):
    db.query(BrandVoice).update({BrandVoice.is_active: False})
    voice = db.query(BrandVoice).filter(BrandVoice.id == id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    voice.is_active = True
    db.commit()
    return {"status": "success", "activated": voice.name}

@router.delete("/brand-voice/{id}")
def delete_brand_voice(id: int, db: Session = Depends(get_db)):
    voice = db.query(BrandVoice).filter(BrandVoice.id == id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    db.delete(voice)
    db.commit()
    return {"status": "success", "message": "Brand voice deleted"}
