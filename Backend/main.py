from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import trends, scripts, content, virality, voiceover, thumbnail, pipeline, reel




load_dotenv()
app = FastAPI(title="Viral Reel Agent")

app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
app.include_router(trends.router)
app.include_router(scripts.router)
app.include_router(content.router)
app.include_router(virality.router)
app.include_router(voiceover.router)
app.include_router(thumbnail.router)
app.include_router(pipeline.router)
app.include_router(reel.router)

@app.get("/")
def root():
    return {"status": "running"}