import os
import re
import numpy as np
import joblib
from sklearn.linear_model import Ridge
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from models import ContentHistory

# Paths for saved models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "saved_models")
os.makedirs(MODEL_DIR, exist_ok=True)

IG_MODEL_PATH = os.path.join(MODEL_DIR, "ig_model.joblib")
LI_MODEL_PATH = os.path.join(MODEL_DIR, "li_model.joblib")

# Category mapping
CATEGORIES = ["tech", "finance", "business", "entertainment", "lifestyle"]

# --- 1. READABILITY SCORER ---
def count_syllables(word: str) -> int:
    word = word.lower().strip()
    if not word:
        return 0
    # Simple syllable counting rules
    vowels = "aeiouy"
    count = 0
    prev_char_is_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_char_is_vowel:
            count += 1
        prev_char_is_vowel = is_vowel
    # Ignore silent 'e' at the end of word
    if word.endswith("e") and count > 1:
        count -= 1
    # Ensure at least 1 syllable
    return max(1, count)

def calculate_readability(text: str) -> float:
    """Calculates Flesch-Kincaid Reading Ease score (0 to 100)."""
    words = [w for w in re.findall(r'\b\w+\b', text) if w]
    sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    
    total_words = len(words)
    total_sentences = max(1, len(sentences))
    
    if total_words == 0:
        return 100.0
        
    total_syllables = sum(count_syllables(w) for w in words)
    
    # Flesch Reading Ease Formula
    score = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
    return round(max(0.0, min(100.0, score)), 2)


# --- 2. SENTIMENT ANALYZER ---
def analyze_sentiment(text: str) -> float:
    """Returns a sentiment score from -1.0 (negative) to 1.0 (positive) based on lexicon mapping."""
    pos_words = {"great", "good", "love", "amazing", "insane", "viral", "success", "innovative", "growing", "best", "perfect", "easy", "simple", "future", "boost", "huge", "smart", "win", "powerful", "free"}
    neg_words = {"bad", "fail", "worst", "mistake", "lose", "risk", "danger", "drop", "waste", "stop", "scam", "wrong", "broke", "scared", "hard", "difficult", "struggle", "poor", "pain", "avoid"}
    
    words = [w.lower() for w in re.findall(r'\b\w+\b', text) if w]
    if not words:
        return 0.0
        
    pos_count = sum(1 for w in words if w in pos_words)
    neg_count = sum(1 for w in words if w in neg_words)
    
    score = (pos_count - neg_count) / max(1, pos_count + neg_count)
    return round(score, 2)


# --- 3. AUDIENCE PERSONA MATCHER ---
def match_personas(topic: str, script_text: str) -> list:
    content = (topic + " " + script_text).lower()
    personas = []
    
    # Keyword criteria for personas
    mappings = {
        "Tech Enthusiasts": ["ai", "tech", "software", "code", "chatgpt", "developer", "robot", "future", "data"],
        "Startup Founders": ["startup", "business", "founder", "saas", "hustle", "revenue", "grow", "funding", "pitch"],
        "Digital Marketers": ["marketing", "social media", "instagram", "views", "brand", "creator", "content", "traffic"],
        "Retail Investors": ["crypto", "finance", "stocks", "invest", "money", "wealth", "passive income", "bitcoin"],
        "General Public": ["lifestyle", "routine", "productivity", "hack", "life", "learn", "study", "tips", "how-to"]
    }
    
    for persona, keywords in mappings.items():
        score = sum(1 for k in keywords if k in content)
        if score > 0:
            personas.append({"name": persona, "confidence": min(score * 25, 100)})
            
    # Sort by confidence
    personas = sorted(personas, key=lambda x: x["confidence"], reverse=True)
    return personas if personas else [{"name": "General Public", "confidence": 75}]


# --- 4. EMOJI RECOMMENDATION ENGINE ---
def recommend_emojis(topic: str, limit: int = 5) -> str:
    content = topic.lower()
    emojis = []
    
    # Simple mapping
    mapping = {
        "ai": ["🤖", "🧠", "💻", "✨"],
        "tech": ["💻", "🚀", "📱", "⚙️"],
        "finance": ["📈", "💰", "💵", "💸", "📊"],
        "crypto": ["🪙", "🔗", "💸"],
        "business": ["💼", "📈", "🤝", "🔥"],
        "startup": ["🚀", "💡", "💰", "⚡"],
        "marketing": ["📣", "🎯", "📈", "📸"],
        "creator": ["🎥", "🎙️", "✨", "🎬"],
        "lifestyle": ["🌱", "✨", "🧘", "☕"],
        "productivity": ["⏱️", "📅", "✅", "⚡"]
    }
    
    for key, val in mapping.items():
        if key in content:
            emojis.extend(val)
            
    # Fallback/General emojis
    emojis.extend(["🔥", "✨", "🚀", "💡", "👀", "👇", "👑", "📈"])
    
    # Deduplicate and limit
    seen = set()
    deduped = [x for x in emojis if not (x in seen or seen.add(x))]
    return "".join(deduped[:limit])


# --- 5. CATEGORY CLASSIFIER ---
def classify_category(topic: str) -> str:
    content = topic.lower()
    
    scores = {cat: 0 for cat in CATEGORIES}
    
    keywords = {
        "tech": ["ai", "gpt", "software", "code", "tech", "developer", "automation", "python", "cyber"],
        "finance": ["finance", "crypto", "invest", "stock", "money", "wealth", "budget", "tax", "passive"],
        "business": ["business", "startup", "founder", "saas", "sales", "revenue", "b2b", "career", "work"],
        "entertainment": ["viral", "movie", "youtube", "music", "game", "gaming", "funny", "meme", "trend"],
        "lifestyle": ["productivity", "routine", "health", "life", "mindset", "gym", "travel", "fitness", "book"]
    }
    
    for cat, words in keywords.items():
        scores[cat] = sum(2 if w in content else 0 for w in words)
        
    best_cat = max(scores, key=scores.get)
    if scores[best_cat] == 0:
        return "tech"  # default
    return best_cat


# --- 6. ML ENGAGEMENT PREDICTION MODEL ---
def generate_synthetic_data(num_samples=1000):
    """Generates synthetic dataset to train initial models."""
    np.random.seed(42)
    
    trend_score = np.random.uniform(30, 100, num_samples)
    word_count = np.random.uniform(40, 150, num_samples)
    sentiment = np.random.uniform(-1, 1, num_samples)
    readability = np.random.uniform(40, 100, num_samples)
    emoji_count = np.random.randint(0, 10, num_samples)
    category = np.random.randint(0, 5, num_samples)
    hook_len = np.random.uniform(10, 80, num_samples)
    
    X = np.column_stack([trend_score, word_count, sentiment, readability, emoji_count, category, hook_len])
    
    # Generate targets (expected metrics) with logical noise
    # Instagram Views = trend_score * 800 + (100 - readability) * 200 + noise
    ig_views = trend_score * 1200 + (100 - readability) * 400 + (sentiment + 1) * 3000 + np.random.normal(0, 5000, num_samples)
    ig_views = np.clip(ig_views, 1000, 500000)
    ig_likes = ig_views * np.random.uniform(0.03, 0.08, num_samples) + emoji_count * 100
    ig_shares = ig_likes * np.random.uniform(0.05, 0.15, num_samples)
    ig_saves = ig_likes * np.random.uniform(0.10, 0.25, num_samples)
    
    y_ig = np.column_stack([ig_views, ig_likes, ig_shares, ig_saves])
    
    # LinkedIn Views
    li_views = trend_score * 200 + (readability) * 100 + (sentiment + 1) * 500 + np.random.normal(0, 1000, num_samples)
    li_views = np.clip(li_views, 500, 100000)
    li_likes = li_views * np.random.uniform(0.01, 0.04, num_samples)
    li_shares = li_likes * np.random.uniform(0.08, 0.20, num_samples)
    li_comments = li_likes * np.random.uniform(0.05, 0.15, num_samples)
    
    y_li = np.column_stack([li_views, li_likes, li_shares, li_comments])
    
    return X, y_ig, y_li

def train_and_save_models():
    """Trains scikit-learn models on synthetic data and saves to disk."""
    X, y_ig, y_li = generate_synthetic_data()
    
    # Using Ridge regression for multi-output forecasting
    ig_model = Ridge()
    ig_model.fit(X, y_ig)
    
    li_model = Ridge()
    li_model.fit(X, y_li)
    
    joblib.dump(ig_model, IG_MODEL_PATH)
    joblib.dump(li_model, LI_MODEL_PATH)
    print("Synthetic ML Models trained and saved successfully.")

# Load models on import or train if missing
if not os.path.exists(IG_MODEL_PATH) or not os.path.exists(LI_MODEL_PATH):
    train_and_save_models()

try:
    ig_predictor = joblib.load(IG_MODEL_PATH)
    li_predictor = joblib.load(LI_MODEL_PATH)
except Exception as e:
    print(f"Error loading models: {e}. Re-training...")
    train_and_save_models()
    ig_predictor = joblib.load(IG_MODEL_PATH)
    li_predictor = joblib.load(LI_MODEL_PATH)

def predict_engagement(trend_score: int, word_count: int, hook: str, script_text: str, category_name: str) -> dict:
    """Uses scikit-learn models to predict views, likes, shares, etc."""
    sentiment = analyze_sentiment(hook)
    readability = calculate_readability(script_text)
    emoji_count = len(re.findall(r'[\u2600-\u27BF]|[\u1F300-\u1F6FF]|[\u1F900-\u1F9FF]', hook + script_text))
    
    cat_idx = CATEGORIES.index(category_name) if category_name in CATEGORIES else 0
    hook_len = len(hook)
    
    # Features match training: [trend_score, word_count, sentiment, readability, emoji_count, category, hook_len]
    features = np.array([[trend_score, word_count, sentiment, readability, emoji_count, cat_idx, hook_len]])
    
    ig_preds = ig_predictor.predict(features)[0]
    li_preds = li_predictor.predict(features)[0]
    
    # Format and bound outputs
    ig_views = int(max(500, ig_preds[0]))
    ig_likes = int(max(20, ig_preds[1]))
    ig_shares = int(max(5, ig_preds[2]))
    ig_saves = int(max(10, ig_preds[3]))
    
    li_views = int(max(100, li_preds[0]))
    li_likes = int(max(5, li_preds[1]))
    li_shares = int(max(1, li_preds[2]))
    li_comments = int(max(1, li_preds[3]))
    
    # Calculate Engagement Rates
    ig_er = round(((ig_likes + ig_shares + ig_saves) / max(1, ig_views)) * 100, 2)
    li_er = round(((li_likes + li_shares + li_comments) / max(1, li_views)) * 100, 2)
    
    # Calculate Virality Score (0-100) based on engagement rates and trend score
    raw_virality = (trend_score * 0.4) + (ig_er * 4) + (li_er * 5) + (readability * 0.1)
    virality_score = int(min(100, max(15, raw_virality)))
    
    return {
        "virality_score": virality_score,
        "readability": readability,
        "sentiment": sentiment,
        "category": category_name,
        "instagram": {
            "views": f"{int(ig_views * 0.8)}-{int(ig_views * 1.2)}",
            "likes": f"{int(ig_likes * 0.8)}-{int(ig_likes * 1.2)}",
            "shares": f"{int(ig_shares * 0.8)}-{int(ig_shares * 1.2)}",
            "saves": f"{int(ig_saves * 0.8)}-{int(ig_saves * 1.2)}",
            "engagement_rate": f"{ig_er}%"
        },
        "linkedin": {
            "views": f"{int(li_views * 0.8)}-{int(li_views * 1.2)}",
            "likes": f"{int(li_likes * 0.8)}-{int(li_likes * 1.2)}",
            "shares": f"{int(li_shares * 0.8)}-{int(li_shares * 1.2)}",
            "comments": f"{int(li_comments * 0.8)}-{int(li_comments * 1.2)}",
            "engagement_rate": f"{li_er}%"
        }
    }


# --- 7. CONTENT SIMILARITY & SATURATION ---
def analyze_saturation(new_topic: str, db: Session) -> dict:
    """Uses TF-IDF + Cosine Similarity from scikit-learn to check topic oversaturation."""
    # Get past 20 completed topics
    past_runs = db.query(ContentHistory).filter(ContentHistory.status == "completed").order_by(ContentHistory.created_at.desc()).limit(20).all()
    past_topics = [run.topic for run in past_runs if run.topic]
    
    if not past_topics:
        return {"saturation_score": 10, "verdict": "Fresh Topic", "similar_past_topics": []}
        
    all_texts = past_topics + [new_topic]
    
    try:
        vectorizer = TfidfVectorizer().fit_transform(all_texts)
        vectors = vectorizer.toarray()
        
        # Cosine similarity between new_topic (last item) and all past topics
        new_vec = vectors[-1].reshape(1, -1)
        similarities = cosine_similarity(vectors[:-1], new_vec).flatten()
        
        # Find similar items
        similar_items = []
        for idx, score in enumerate(similarities):
            if score > 0.25:
                similar_items.append({"topic": past_topics[idx], "similarity": round(float(score), 2)})
                
        max_similarity = float(np.max(similarities)) if len(similarities) > 0 else 0.0
        saturation_score = int(max_similarity * 100)
        
        if saturation_score > 70:
            verdict = "Oversaturated"
        elif saturation_score > 40:
            verdict = "Moderate Saturation"
        else:
            verdict = "Fresh Topic"
            
        return {
            "saturation_score": max(5, saturation_score),
            "verdict": verdict,
            "similar_past_topics": sorted(similar_items, key=lambda x: x["similarity"], reverse=True)[:3]
        }
    except Exception as e:
        print(f"Similarity analysis error: {e}")
        return {"saturation_score": 15, "verdict": "Fresh Topic", "similar_past_topics": []}


# --- 8. TREND VELOCITY CLASSIFIER ---
def classify_velocity(score: int, comments: int) -> str:
    """Classifies if a trend is rising, peak, or declining."""
    # Heuristics based on engagement signals
    if score > 10000 or comments > 500:
        return "peak"
    elif score > 2000 or comments > 100:
        return "rising"
    else:
        return "declining"


# --- 9. OPTIMAL POSTING TIME PREDICTOR ---
def predict_posting_time(category: str, velocity: str) -> dict:
    """Predicts optimal posting windows per platform based on topic category."""
    times = {
        "tech": {
            "instagram": "Monday/Wednesday 6:00 PM - 8:00 PM",
            "linkedin": "Tuesday/Thursday 9:00 AM - 11:00 AM"
        },
        "finance": {
            "instagram": "Sunday/Thursday 7:00 PM - 9:00 PM",
            "linkedin": "Monday/Wednesday 8:00 AM - 10:00 AM"
        },
        "business": {
            "instagram": "Tuesday 12:00 PM - 2:00 PM",
            "linkedin": "Tuesday/Wednesday 8:30 AM - 10:30 AM"
        },
        "entertainment": {
            "instagram": "Friday/Saturday 8:00 PM - 11:00 PM",
            "linkedin": "Thursday 12:00 PM - 1:00 PM"
        },
        "lifestyle": {
            "instagram": "Saturday/Sunday 9:00 AM - 11:00 AM",
            "linkedin": "Friday 9:00 AM - 11:00 AM"
        }
    }
    
    cat = category.lower()
    base_times = times.get(cat, times["tech"])
    
    # If the trend velocity is peak or rising, we recommend posting ASAP
    if velocity in ["peak", "rising"]:
        return {
            "instagram": f"ASAP / Next peak slot ({base_times['instagram']})",
            "linkedin": f"ASAP / Next peak slot ({base_times['linkedin']})"
        }
    return base_times
