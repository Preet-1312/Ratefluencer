import datetime
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Boolean
from db import Base

class ContentHistory(Base):
    __tablename__ = "content_history"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True, nullable=False)
    topic = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)
    current_step = Column(String, default="")
    trend_score = Column(Integer, default=0)
    virality_score = Column(Integer, default=0)
    
    script = Column(JSON, nullable=True)
    linkedin = Column(JSON, nullable=True)
    instagram = Column(JSON, nullable=True)
    virality = Column(JSON, nullable=True)
    voiceover = Column(JSON, nullable=True)
    thumbnail = Column(JSON, nullable=True)
    broll = Column(JSON, nullable=True)
    subtitles = Column(JSON, nullable=True)
    srt = Column(Text, nullable=True)
    video = Column(JSON, nullable=True)
    youtube_clips = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class BrandVoice(Base):
    __tablename__ = "brand_voice"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    tone = Column(String, nullable=False)  # professional, casual, bold, techy, witty
    style_guide = Column(Text, nullable=False)
    hashtags = Column(String, default="")  # comma-separated hashtags
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=False)
