import os
from dotenv import load_dotenv
from openai import OpenAI
import re

# Load .env variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_OPENAI = os.getenv("USE_OPENAI_MODERATION", "True").lower() == "true"

client = OpenAI(api_key=OPENAI_API_KEY)


# ----------------------------
# 🧩 OpenAI Moderation
# ----------------------------
def openai_moderate(text: str):
    """Use OpenAI's omni-moderation-latest model."""
    try:
        response = client.moderations.create(
            model="omni-moderation-latest",
            input=text
        )
        result = response.results[0]
        return {
            "model": "omni-moderation-latest",
            "unsafe": result["flagged"],
            "categories": result["categories"]
        }
    except Exception as e:
        return {
            "model": "omni-moderation-latest",
            "error": str(e),
            "unsafe": False,
            "categories": {}
        }


# ----------------------------
# 🧩 Llama Guard (local fallback)
# ----------------------------
def llama_guard_moderate(text: str):
    """Simulated Llama Guard moderation for local/offline fallback."""
    keywords = ["hate", "violence", "attack", "awful", "kill"]
    unsafe = any(word in text.lower() for word in keywords)
    return {
        "model": "llama_guard_3",
        "unsafe": unsafe,
        "categories": {"violence": unsafe, "hate_speech": unsafe, "sexual": False}
    }


# ----------------------------
# 🧠 Civility (mock or local)
# ----------------------------
import re

def contentguard_score(text: str):
    """
    Heuristic civility scorer.
    1. start from 1.0
    2. deduct if insulting / aggressive
    3. deduct if profanity
    """

    lowered = text.lower()
    score = 1.0  # assume polite

    # harsh insult / abusive language
    severe_toxic_words = [
        "idiot", "stupid", "dumb", "awful", "hate",
        "trash", "shut up", "kill yourself", "attack", "hurt"
    ]
    if any(word in lowered for word in severe_toxic_words):
        score -= 0.6  # heavy penalty

    # mild frustration / irritation
    mild_rude_phrases = [
        "annoying", "what the hell", "wth", "wtf", "this sucks",
        "so rude", "stop interrupting", "kind of dumb"
    ]
    if any(phrase in lowered for phrase in mild_rude_phrases):
        score -= 0.3

    # floor at 0.0, cap at 1.0
    score = max(0.0, min(score, 1.0))

    return {
        "model": "contentguard",
        "civility_score": round(score, 2)
    }

# ----------------------------
# 😊 Sentiment (mock for now)
# ----------------------------
def sentiment_analysis(text: str):
    sentiment = "positive" if "good" in text.lower() else "negative" if "hate" in text.lower() else "neutral"
    return {"model": "sentiment_v1", "sentiment": sentiment}
