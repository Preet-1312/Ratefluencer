import requests
import xml.etree.ElementTree as ET
import json

def get_hacker_news_trends():
    trends = []
    try:
        # Get top stories
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return []
        story_ids = response.json()[:15] # Top 15 stories
        
        for story_id in story_ids:
            try:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_res = requests.get(story_url, timeout=2)
                if story_res.status_code == 200:
                    story = story_res.json()
                    title = story.get("title", "")
                    
                    # Filter keywords to make it highly relevant to AI/Tech
                    keywords = [
                        "ai", "tech", "startup", "developer", "programming", "llm", "gpt", 
                        "model", "code", "software", "web", "app", "cloud", "saas", "hacker",
                        "neural", "gpu", "silicon", "open-source", "python", "javascript", "rust"
                    ]
                    title_lower = title.lower()
                    is_relevant = any(k in title_lower for k in keywords)
                    
                    trends.append({
                        "source": "HackerNews",
                        "title": title,
                        "score": story.get("score", 50),
                        "comments": story.get("descendants", 0),
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        "is_relevant": is_relevant
                    })
            except Exception as e:
                print(f"HN single story error {story_id}: {e}")
    except Exception as e:
        print(f"HN fetch error: {e}")
    
    # Sort relevant ones first
    trends.sort(key=lambda x: (x["is_relevant"], x["score"]), reverse=True)
    for t in trends:
        t.pop("is_relevant", None)
    return trends[:6]

def get_dev_to_trends():
    trends = []
    try:
        url = "https://dev.to/api/articles?per_page=15"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            posts = response.json()
            for post in posts:
                title = post.get("title", "")
                trends.append({
                    "source": "Dev.to",
                    "title": title,
                    "score": post.get("public_reactions_count", 30),
                    "comments": post.get("comments_count", 0),
                    "url": post.get("url", "")
                })
    except Exception as e:
        print(f"Dev.to fetch error: {e}")
    return trends[:6]

def get_techcrunch_trends():
    trends = []
    try:
        url = "https://techcrunch.com/feed/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            # Parse XML
            root = ET.fromstring(response.content)
            items = root.findall(".//item")
            for item in items[:10]:
                title = item.find("title")
                link = item.find("link")
                
                title_text = title.text if title is not None else ""
                link_text = link.text if link is not None else ""
                
                trends.append({
                    "source": "TechCrunch",
                    "title": title_text,
                    "score": 150, # Static high score for TC Front Page
                    "comments": 10,
                    "url": link_text
                })
    except Exception as e:
        print(f"TechCrunch fetch error: {e}")
    return trends[:6]

def get_reddit_trends():
    """
    Wrapper function to remain fully backwards-compatible with existing backend files.
    Fetches real-time tech trends from HackerNews, Dev.to, and TechCrunch RSS feeds.
    """
    trends = []
    
    # 1. Fetch HackerNews
    try:
        trends += get_hacker_news_trends()
    except Exception as e:
        print(f"Failed to fetch HackerNews: {e}")
        
    # 2. Fetch Dev.to
    try:
        trends += get_dev_to_trends()
    except Exception as e:
        print(f"Failed to fetch Dev.to: {e}")
        
    # 3. Fetch TechCrunch
    try:
        trends += get_techcrunch_trends()
    except Exception as e:
        print(f"Failed to fetch TechCrunch: {e}")
        
    return trends