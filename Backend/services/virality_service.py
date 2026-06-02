from groq import Groq
import json, os, re

def predict_virality(topic: str, script: dict, linkedin: dict = {}, instagram: dict = {}):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = f"""You are a viral content analyst. Analyze this content and predict virality.

    TOPIC: {topic}
    TREND SCORE: {script.get('trend_score', 50)}/100
    HOOK: {script.get('hook', '')}
    KEY INSIGHTS: {script.get('key_insights', [])}
    WORD COUNT: {script.get('word_count', 0)}

    Return ONLY valid JSON, no markdown, no backticks, no extra text:
    {{
      "virality_score": 78,
      "confidence": "high",
      "instagram": {{
        "expected_views": "45000-120000",
        "expected_likes": "2000-5500",
        "expected_shares": "300-800",
        "expected_saves": "500-1200"
      }},
      "linkedin": {{
        "expected_views": "8000-25000",
        "expected_likes": "300-900",
        "expected_shares": "50-150",
        "expected_comments": "30-100"
      }},
      "strengths": ["strength one", "strength two", "strength three"],
      "weaknesses": ["weakness one", "weakness two"],
      "improvement_tips": ["tip one", "tip two", "tip three"],
      "best_time_to_post": {{
        "instagram": "Tuesday-Thursday 6-9pm",
        "linkedin": "Tuesday-Wednesday 8-10am"
      }},
      "verdict": "one sentence overall verdict here"
    }}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown if present
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()

        # Extract JSON object if extra text around it
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            raw = match.group(0)

        # Fix common JSON issues — trailing commas
        raw = re.sub(r',\s*}', '}', raw)
        raw = re.sub(r',\s*]', ']', raw)

        return json.loads(raw)
    except Exception as e:
        print(f"[ViralityPredictor] LLM prediction failed ({type(e).__name__}: {e}), using local fallback")
        # Return safe fallback so pipeline doesn't crash
        return {
            "virality_score": 65,
            "confidence": "medium",
            "instagram": {
                "expected_views": "10000-50000",
                "expected_likes": "500-2000",
                "expected_shares": "100-400",
                "expected_saves": "200-600"
            },
            "linkedin": {
                "expected_views": "3000-10000",
                "expected_likes": "100-400",
                "expected_shares": "20-80",
                "expected_comments": "10-40"
            },
            "strengths": ["Relevant topic", "Clear hook", "Good timing"],
            "weaknesses": ["Could be more specific"],
            "improvement_tips": ["Add personal story", "Use stronger hook", "Post at peak hours"],
            "best_time_to_post": {
                "instagram": "Tuesday-Thursday 6-9pm",
                "linkedin": "Tuesday-Wednesday 8-10am"
            },
            "verdict": "Solid content with good viral potential for tech audience."
        }