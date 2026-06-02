from groq import Groq
import json, os, re

def generate_linkedin_post(topic: str, script: dict, brand_voice_style: str = None):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        voice_instruction = f"\nBrand Voice Styling Guide: {brand_voice_style}" if brand_voice_style else ""

        prompt = f"""You are a LinkedIn content expert who writes viral professional posts.
        
        Topic: {topic}
        Hook: {script.get('hook', '')}
        Key Insights: {script.get('key_insights', [])}
        {voice_instruction}
        
        Write a LinkedIn post that will go viral among tech/AI/startup professionals.
        
        Return ONLY this JSON, no markdown, no backticks, no extra text:
        {{
          "post": "full linkedin post text with line breaks using \\n",
          "hashtags": ["#AI", "#Technology"],
          "engagement_hook": "one question to ask in comments",
          "char_count": 0
        }}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.5
        )
        raw = response.choices[0].message.content.strip()
        
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()

        # Extract JSON object using regex
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            raw = match.group(0)

        # Fix common JSON issues
        raw = re.sub(r',\s*}', '}', raw)
        raw = re.sub(r',\s*]', ']', raw)

        result = json.loads(raw)
    except Exception as e:
        print(f"[LinkedInPost] LLM generation failed ({type(e).__name__}: {e}), using local fallback")
        result = {
            "post": f"🚀 Exciting insights on {topic}!\n\nHere is what you need to know:\n" + "\n".join(f"- {i}" for i in script.get('key_insights', [])),
            "hashtags": ["#AI", "#Tech", "#Growth"],
            "engagement_hook": f"What are your thoughts on {topic}?",
            "char_count": 0
        }

    # Normalize response key name to post_text (if post is returned)
    if "post" in result:
        result["post_text"] = result["post"]
    elif "post_text" not in result:
        result["post_text"] = ""
        
    result["char_count"] = len(result.get("post_text", ""))
    return result


def generate_instagram_caption(topic: str, script: dict, brand_voice_style: str = None):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        voice_instruction = f"\nBrand Voice Styling Guide: {brand_voice_style}" if brand_voice_style else ""

        prompt = f"""You are an Instagram Reels content expert who writes viral captions.
        
        Topic: {topic}
        Hook: {script.get('hook', '')}
        Key Insights: {script.get('key_insights', [])}
        {voice_instruction}
        
        Write a punchy Instagram caption with emojis, CTA, and hashtags.
        
        Return ONLY this JSON, no markdown, no backticks, no extra text:
        {{
          "caption": "caption text with emojis and line breaks using \\n",
          "hashtags": ["#ai", "#tech"],
          "cta": "save this / comment below / follow for more",
          "char_count": 0
        }}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.5
        )
        raw = response.choices[0].message.content.strip()
        
        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "").strip()

        # Extract JSON object using regex
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            raw = match.group(0)

        # Fix common JSON issues
        raw = re.sub(r',\s*}', '}', raw)
        raw = re.sub(r',\s*]', ']', raw)

        result = json.loads(raw)
    except Exception as e:
        print(f"[InstagramCaption] LLM generation failed ({type(e).__name__}: {e}), using local fallback")
        result = {
            "caption": f"💡 Quick guide to {topic}! {script.get('hook', '')}\n\nKey details:\n" + "\n".join(f"- {i}" for i in script.get('key_insights', [])),
            "hashtags": ["#ai", "#technology"],
            "cta": "Follow for more daily AI content!",
            "char_count": 0
        }

    # Normalize response key name to caption_text
    if "caption" in result:
        result["caption_text"] = result["caption"]
    elif "caption_text" not in result:
        result["caption_text"] = ""
        
    result["char_count"] = len(result.get("caption_text", ""))
    return result