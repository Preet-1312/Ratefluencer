from groq import Groq
import json, os, re

def generate_script(topic: str, trend_score: int = 50, duration: int = 60, brand_voice_style: str = None):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        word_count = 130 if duration == 60 else (190 if duration == 90 else 70)

        voice_instruction = f"\nBrand Voice Styling Guide: {brand_voice_style}" if brand_voice_style else ""

        prompt = f"""You are a viral short-form video scriptwriter.
        Topic: {topic}
        Target: {duration} seconds (~{word_count} words)
        {voice_instruction}
        
        Return ONLY this JSON, no markdown, no backticks, no extra text:
        {{
          "hook": "attention grabbing 3-second hook sentence",
          "story": "short narrative or explanation flow",
          "key_insights": ["insight one", "insight two", "insight three"],
          "cta": "strong final call to action",
          "full_script": "combined narration script text flow",
          "word_count": 0,
          "estimated_duration_sec": 0
        }}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.5
        )
        raw = response.choices[0].message.content.strip()
        
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()

        # Extract JSON object using regex
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            raw = match.group(0)

        # Fix common JSON issues
        raw = re.sub(r',\s*}', '}', raw)
        raw = re.sub(r',\s*]', ']', raw)

        script = json.loads(raw)
    except Exception as e:
        print(f"[ScriptGenerator] LLM generation failed ({type(e).__name__}: {e}), using local fallback")
        # Fallback script
        script = {
            "hook": f"Here is what you need to know about {topic}.",
            "story": f"We analyzed the trends and found key insights that will change your perspective on {topic}.",
            "key_insights": [f"Insight 1 about {topic}", f"Insight 2 about {topic}", f"Insight 3 about {topic}"],
            "cta": "Follow for more daily insights!",
            "full_script": f"Here is what you need to know about {topic}. We analyzed the trends and found key insights that will change your perspective. Insight 1: details. Insight 2: details. Insight 3: details. Follow for more daily insights!",
            "word_count": 0,
            "estimated_duration_sec": duration
        }

    words = len(script.get("full_script", "").split())
    script["word_count"] = words
    script["estimated_duration_sec"] = round(words / 2.3)
    script["topic"] = topic
    script["trend_score"] = trend_score
    return script