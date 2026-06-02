from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from db import Base, engine
from routers import trends, scripts, content, virality, voiceover, thumbnail, pipeline, reel, websocket, export, features, clips

# Load env variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Viral Reel Agent")

# Allow requests from standard frontend ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(trends.router)
app.include_router(scripts.router)
app.include_router(content.router)
app.include_router(virality.router)
app.include_router(voiceover.router)
app.include_router(thumbnail.router)
app.include_router(pipeline.router)
app.include_router(reel.router)
app.include_router(websocket.router)
app.include_router(export.router)
app.include_router(features.router)
app.include_router(clips.router)

@app.get("/")
def root():
    return {"status": "running", "database": str(engine.url)}