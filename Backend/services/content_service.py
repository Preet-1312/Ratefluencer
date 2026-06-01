from groq import Groq
import json, os

def generate_linkedin_post(topic: str, script: dict):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are a LinkedIn content expert who writes viral professional posts.

Topic: {topic}
Hook: {script.get('hook', '')}
Key Insights: {script.get('key_insights', [])}

Write a LinkedIn post that will go viral among tech/AI/startup professionals.

Return ONLY this JSON, no markdown, no backticks:
{{
  "post": "full linkedin post text with line breaks using \\n",
  "hashtags": ["#AI", "#Technology"],
  "engagement_hook": "one question to ask in comments",
  "char_count": 0
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    raw = response.choices[0].message.content.strip()
    if "```" in raw:
        raw = raw.split("```")[1].replace("json", "").strip()
    result = json.loads(raw)
    result["char_count"] = len(result["post"])
    return result


def generate_instagram_caption(topic: str, script: dict):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are an Instagram Reels content expert who writes viral captions.

Topic: {topic}
Hook: {script.get('hook', '')}
Key Insights: {script.get('key_insights', [])}

Write a punchy Instagram caption with emojis, CTA, and hashtags.

Return ONLY this JSON, no markdown, no backticks:
{{
  "caption": "caption text with emojis and line breaks using \\n",
  "hashtags": ["#ai", "#tech"],
  "cta": "save this / comment below / follow for more",
  "char_count": 0
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    raw = response.choices[0].message.content.strip()
    if "```" in raw:
        raw = raw.split("```")[1].replace("json", "").strip()
    result = json.loads(raw)
    result["char_count"] = len(result["caption"])
    return result