import os
import json
import re
from groq import Groq

def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_competitors(topic: str) -> list:
    client = get_groq_client()
    prompt = f"""You are a competitor social analyst. Analyze the top 5 viral competitor reels on the topic: "{topic}".
    
    Return a valid JSON array of 5 competitors. Return ONLY valid JSON, no markdown, no backticks, no extra text.
    Format:
    [
      {{
        "competitor_name": "@creator_handle",
        "hook_style": "How they hooked the user in 3 seconds",
        "video_flow": "Visual style, music choice, and pacing details",
        "estimated_views": "500K+",
        "why_it_worked": "Analysis of hook strength and visual hooks used",
        "key_takeaway": "What we should copy or adapt from this video"
      }},
      ...
    ]"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.4
        )
        raw = response.choices[0].message.content.strip()
        
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            raw = match.group(0)
            
        # trailing commas
        raw = re.sub(r',\s*\]', ']', raw)
        raw = re.sub(r',\s*\}', '}', raw)
        
        return json.loads(raw)
    except Exception as e:
        print(f"Competitor analysis error: {e}")
        # Return fallback
        return [
            {
                "competitor_name": f"@industry_leader_{i+1}",
                "hook_style": f"Highly visual statement about {topic}",
                "video_flow": "Fast-paced jumps, overlay text, high energy lo-fi beats",
                "estimated_views": "250K - 1M",
                "why_it_worked": "Capitalized on trending topic with direct bold styling.",
                "key_takeaway": "Keep video duration under 45 seconds and focus on rapid transitions."
            } for i in range(5)
        ]


def generate_content_calendar(topic: str, brand_voice: str = "Standard") -> list:
    client = get_groq_client()
    prompt = f"""You are a content strategist. Create a 7-day content calendar from the topic: "{topic}".
    The brand tone is: {brand_voice}.
    
    For each day, provide:
    - Day (Day 1 to Day 7)
    - Sub-topic / Title
    - Platforms (e.g. LinkedIn, Instagram, TikTok, Shorts)
    - Caption angle / Summary
    - Suggested Hook
    - Visual description / B-roll instruction
    
    Return a valid JSON array of 7 objects. Return ONLY valid JSON, no markdown, no backticks.
    Format:
    [
      {{
        "day": "Day 1",
        "title": "Subtopic Title",
        "platforms": ["Instagram", "TikTok"],
        "angle": "What this post is about",
        "hook": "Suggested hook text",
        "visual": "B-roll suggestion"
      }},
      ...
    ]"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.4
        )
        raw = response.choices[0].message.content.strip()
        
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            raw = match.group(0)
            
        raw = re.sub(r',\s*\]', ']', raw)
        raw = re.sub(r',\s*\}', '}', raw)
        
        return json.loads(raw)
    except Exception as e:
        print(f"Content calendar error: {e}")
        return [
            {
                "day": f"Day {i+1}",
                "title": f"Sub-topic {i+1} for {topic}",
                "platforms": ["Instagram", "LinkedIn"],
                "angle": f"Educational breakdown of sub-topic {i+1}",
                "hook": f"Here is the secret about {topic} you didn't know...",
                "visual": "Aesthetic workstation background with dynamic text overlays."
            } for i in range(7)
        ]


def repurpose_content(topic: str, script: dict) -> dict:
    client = get_groq_client()
    hook = script.get("hook", topic)
    story = script.get("story", "")
    insights = "\n".join(f"- {i}" for i in script.get("key_insights", []))
    cta = script.get("cta", "")
    
    prompt = f"""You are a multi-platform content copywriter. Repurpose this short reel script outline into 3 formats:
    1. A detailed SEO-friendly Blog Post (approx. 300 words, split into headings).
    2. A Tweet Thread (4-5 cohesive tweets, numbered, incorporating emojis and hooks).
    3. A personal, conversational Email Newsletter (approx. 200 words, with a subject line and CTA).
    
    TOPIC: {topic}
    HOOK: {hook}
    STORY: {story}
    KEY INSIGHTS: {insights}
    CTA: {cta}
    
    Return a valid JSON object. Return ONLY valid JSON, no markdown, no backticks.
    Format:
    {{
      "blog_post": {{
        "title": "Blog Title",
        "content": "Blog HTML/Markdown text with headings..."
      }},
      "tweet_thread": [
        "Tweet 1 text...",
        "Tweet 2 text...",
        ...
      ],
      "newsletter": {{
        "subject": "Newsletter Subject Line",
        "body": "Newsletter body text here..."
      }}
    }}"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2500,
            temperature=0.5
        )
        raw = response.choices[0].message.content.strip()
        
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            raw = match.group(0)
            
        raw = re.sub(r',\s*\}', '}', raw)
        raw = re.sub(r',\s*\]', ']', raw)
        
        return json.loads(raw)
    except Exception as e:
        print(f"Repurposing error: {e}")
        return {
            "blog_post": {
                "title": f"Why {topic} is Changing Everything",
                "content": f"## Introduction\n{topic} is reshaping our workflow.\n\n## Key Takeaways\n- Focus on quality.\n- Scale with AI.\n\n## Conclusion\nAct fast."
            },
            "tweet_thread": [
                f"1/ Thread: Let's talk about {topic}. Why is it exploding right now? 🧵👇",
                f"2/ The secret lies in script layout and B-roll hook consistency. Most creators get this wrong.",
                f"3/ Start with a 3-second hook, build a short relatable story, and close with a strong CTA.",
                f"4/ Read the full breakdown in our newsletter. Link in bio! 📈🚀"
            ],
            "newsletter": {
                "subject": f"The complete playbook on {topic} inside",
                "body": f"Hey Friends,\n\n{topic} is taking over. In this issue, we break down our formula for script hooks, b-roll assembly, and virality forecasting.\n\nBest,\nTeam Ratefluencer"
            }
        }


def generate_reel_series(topic: str) -> list:
    client = get_groq_client()
    prompt = f"""You are a video script planner. Generate a 5-part video series outline from the topic: "{topic}".
    Each episode is a 30-60 second standalone reel, but together they form a complete course/series.
    
    Provide:
    - Episode Number (Part 1 to Part 5)
    - Episode Title
    - Hook Idea
    - Brief Storyline Outline
    - Call to Action
    
    Return a valid JSON array of 5 objects. Return ONLY valid JSON, no markdown, no backticks.
    Format:
    [
      {{
        "part": 1,
        "title": "Part 1 Title",
        "hook": "Hook statement",
        "storyline": "Details of the video contents",
        "cta": "Call to action for Part 2"
      }},
      ...
    ]"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.4
        )
        raw = response.choices[0].message.content.strip()
        
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            raw = match.group(0)
            
        raw = re.sub(r',\s*\]', ']', raw)
        raw = re.sub(r',\s*\}', '}', raw)
        
        return json.loads(raw)
    except Exception as e:
        print(f"Reel series error: {e}")
        return [
            {
                "part": i + 1,
                "title": f"Part {i+1}: Mastering {topic}",
                "hook": f"This is Part {i+1} of my {topic} blueprint.",
                "storyline": f"Detailed step {i+1} explanation.",
                "cta": f"Like and follow for Part {i+2 if i < 4 else 'the next series'}!"
            } for i in range(5)
        ]
