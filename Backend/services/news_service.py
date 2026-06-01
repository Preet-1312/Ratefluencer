import requests
import os

def get_news_trends():
    api_key = os.getenv("NEWS_API_KEY")
    queries = ["artificial intelligence", "tech startup", "creator economy"]
    trends = []
    for q in queries:
        url = (
            f"https://newsapi.org/v2/everything"
            f"?q={q}&sortBy=publishedAt&pageSize=5"
            f"&language=en&apiKey={api_key}"
        )
        res = requests.get(url).json()
        for article in res.get("articles", []):
            trends.append({
                "source": f"news/{article['source']['name']}",
                "title": article["title"],
                "score": 0,
                "comments": 0,
                "url": article["url"]
            })
    return trends