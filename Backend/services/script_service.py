from groq import Groq
import json, os

def generate_script(topic: str, trend_score: int = 50, duration: int = 60):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    word_count = 130 if duration == 60 else 70

    prompt = f"""You are a viral short-form video scriptwriter.
Topic: {topic}
Target: {duration} seconds (~{word_count} words)

Return ONLY this JSON, no markdown, no backticks:
{{
  "hook": "...",
  "story": "...",
  "key_insights": ["...", "...", "..."],
  "cta": "...",
  "full_script": "...",
  "word_count": 0,
  "estimated_duration_sec": 0
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    raw = response.choices[0].message.content.strip()
    if "```" in raw:
        raw = raw.split("```")[1].replace("json", "").strip()

    script = json.loads(raw)
    words = len(script["full_script"].split())
    script["word_count"] = words
    script["estimated_duration_sec"] = round(words / 2.3)
    script["topic"] = topic
    script["trend_score"] = trend_score
    return script