import base64
import os
import requests
from urllib.parse import quote

def generate_thumbnail(topic: str, hook: str = ""):
    try:
        prompt = f"Professional viral social media thumbnail, {topic}, bold cinematic style, dark background, bright neon accent colors, 9x16 vertical, dramatic lighting, no text, high quality"
        
        encoded_prompt = quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=576&height=1024&nologo=true"
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            image_b64 = base64.b64encode(response.content).decode("utf-8")
            return {
                "image_base64": image_b64,
                "format": "jpeg",
                "prompt_used": prompt[:120] + "...",
                "topic": topic,
                "fallback": False
            }
        else:
            return {"image_base64": None, "fallback": True, "error": f"Status {response.status_code}"}

    except Exception as e:
        return {"image_base64": None, "fallback": True, "error": str(e)}