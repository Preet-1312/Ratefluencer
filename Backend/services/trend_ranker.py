from groq import Groq
import json, os, re, math

# ---------------------------------------------------------------------------
# High-value keywords for local scoring fallback
# ---------------------------------------------------------------------------
VIRAL_KEYWORDS = [
    "ai", "gpt", "llm", "openai", "anthropic", "gemini", "copilot", "neural",
    "startup", "launch", "funding", "billion", "million", "open-source",
    "developer", "programming", "python", "javascript", "rust", "react",
    "cloud", "saas", "gpu", "silicon", "apple", "google", "meta", "microsoft",
    "hack", "security", "breach", "crypto", "blockchain", "agent", "autonomous",
    "viral", "trend", "breaking", "exclusive", "leaked", "new", "first",
]

SOURCE_WEIGHTS = {
    "HackerNews": 1.2,
    "Dev.to": 1.0,
    "TechCrunch": 1.4,
    "NewsAPI": 1.1,
    "YouTube": 0.9,
}


def _local_rank(raw_trends: list) -> list:
    """
    Smart fallback ranker — no LLM needed.
    Uses engagement score, comment count, source weight, and keyword relevance.
    """
    results = []
    for t in raw_trends[:20]:
        title_lower = t.get("title", "").lower()
        engagement = min(t.get("score", 0), 500)  # cap at 500
        comments = min(t.get("comments", 0), 200)  # cap at 200
        source_w = SOURCE_WEIGHTS.get(t.get("source", ""), 1.0)

        # Keyword hits (0-1 range, more hits = higher)
        hits = sum(1 for kw in VIRAL_KEYWORDS if kw in title_lower)
        keyword_score = min(hits / 4.0, 1.0)  # 4+ keywords = max

        # Normalize engagement to 0-1 (log scale so 10 and 500 both matter)
        eng_norm = math.log1p(engagement) / math.log1p(500)

        # Normalize comments to 0-1
        cmt_norm = math.log1p(comments) / math.log1p(200)

        # Weighted composite → 0-100
        raw_score = (
            eng_norm * 35 +
            cmt_norm * 20 +
            keyword_score * 30 +
            source_w * 12
        )
        trend_score = max(10, min(98, int(raw_score)))

        reason = f"Engagement-based ({t.get('source', 'web')})"
        results.append({
            **t,
            "trend_score": trend_score,
            "reason": reason,
        })

    return sorted(results, key=lambda x: x["trend_score"], reverse=True)


def rank_trends(raw_trends: list):
    if not raw_trends:
        return []

    # --- Try LLM-powered ranking first ---
    try:
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

        scored = json.loads(raw)

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

    except Exception as e:
        # --- Graceful fallback: local scoring (rate limit, network, parse errors) ---
        print(f"[TrendRanker] LLM ranking failed ({type(e).__name__}: {e}), using local scoring fallback")
        return _local_rank(raw_trends)