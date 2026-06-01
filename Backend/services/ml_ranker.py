import numpy as np
from pytrends.request import TrendReq
from sklearn.preprocessing import MinMaxScaler

def get_google_trend_score(keyword: str) -> float:
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload([keyword[:100]], timeframe='now 7-d')
        data = pytrends.interest_over_time()
        if data.empty:
            return 50.0
        values = data[keyword[:100]].values
        recent = float(np.mean(values[-3:]))
        older = float(np.mean(values[:3])) + 1
        velocity = min((recent / older) * 50, 100)
        return round(velocity, 2)
    except:
        return 50.0

def ml_score(trend: dict, llm_score: int) -> dict:
    scaler = MinMaxScaler(feature_range=(0, 100))

    engagement = min(trend.get("score", 0) / 1000, 100)
    comments = min(trend.get("comments", 0) / 100, 100)
    google_velocity = get_google_trend_score(trend.get("title", "")[:50])

    raw = np.array([[engagement, comments, google_velocity, llm_score]])
    weights = np.array([0.15, 0.10, 0.35, 0.40])
    final_score = float(np.dot(raw[0] / 100, weights) * 100)

    return {
        "ml_score": round(final_score),
        "signals": {
            "engagement": round(engagement),
            "comments_signal": round(comments),
            "google_velocity": round(google_velocity),
            "llm_score": llm_score
        }
    }