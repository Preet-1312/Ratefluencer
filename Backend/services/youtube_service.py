from googleapiclient.discovery import build
import os

def get_youtube_trends():
    youtube = build("youtube", "v3",
                    developerKey=os.getenv("YOUTUBE_API_KEY"))
    request = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        regionCode="US",
        videoCategoryId="28",
        maxResults=10
    )
    response = request.execute()
    trends = []
    for item in response.get("items", []):
        trends.append({
            "source": "youtube",
            "title": item["snippet"]["title"],
            "score": int(item["statistics"].get("viewCount", 0)),
            "comments": int(item["statistics"].get("commentCount", 0)),
            "url": f"https://youtube.com/watch?v={item['id']}"
        })
    return trends