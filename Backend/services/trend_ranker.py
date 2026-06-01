from groq import Groq
import json, os, re

def rank_trends(raw_trends: list):
    if not raw_trends:
        return []

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    titles = [t["title"] for t in raw_trends[:20]]

    prompt = f"""You are a viral content expert. Score each trend title 0-100.

Titles:
{json.dumps(titles, indent=2)}

Rules:
- Score based on: Growth Velocity, Novelty, Engagement Potential, Audience Relevance
- Keep reason under 8 words
- Return ONLY a JSON array, no markdown, no backticks

Format:
[{{"title": "exact title here", "score": 85, "reason": "short reason"}}, ...]"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.1
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown
    if "```" in raw:
        raw = raw.split("```")[1].replace("json", "").strip()

    # Extract JSON array
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if match:
        raw = match.group(0)

    # Fix trailing commas
    raw = re.sub(r',\s*\]', ']', raw)
    raw = re.sub(r',\s*\}', '}', raw)

    try:
        scored = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback — return raw trends with default score
        return [{**t, "trend_score": 50, "reason": "scoring failed"} for t in raw_trends[:10]]

    result = []
    for item in scored:
        original = next((t for t in raw_trends if t["title"] == item["title"]), {})
        if not original:
            original = {"title": item["title"], "source": "unknown", "score": 0, "comments": 0}
        result.append({
            **original,
            "trend_score": item.get("score", 50),
            "reason": item.get("reason", "")
        })

    return sorted(result, key=lambda x: x["trend_score"], reverse=True)