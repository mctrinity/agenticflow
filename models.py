import re

def llama_guard_moderate(text: str):
    """Simulated Llama Guard moderation model"""
    categories = {
        "hate_speech": bool(re.search(r"\bhate\b", text, re.I)),
        "violence": bool(re.search(r"\b(kill|attack|fight)\b", text, re.I)),
        "sexual": bool(re.search(r"\b(sex|porn|nude)\b", text, re.I))
    }
    unsafe = any(categories.values())
    return {
        "model": "llama_guard_3",
        "unsafe": unsafe,
        "categories": categories
    }

def contentguard_score(text: str):
    """Enhanced civility scoring with tone detection."""
    rude_words = ["idiot", "stupid", "hate", "ugly", "dumb"]
    negative_tone = ["annoying", "boring", "bad", "terrible", "awful", "interrupting"]

    lower_text = text.lower()
    rude_hits = sum(lower_text.count(w) for w in rude_words)
    tone_hits = sum(lower_text.count(w) for w in negative_tone)

    total_hits = rude_hits + tone_hits
    word_count = max(len(text.split()), 1)
    civility = max(0, 1 - (total_hits / word_count))

    cleaned_text = text
    for w in rude_words:
        cleaned_text = cleaned_text.replace(w, "[redacted]")

    return {
        "model": "contentguard",
        "civility_score": round(civility, 2),
        "modified_text": cleaned_text
    }


def sentiment_analysis(text: str):
    """Enhanced sentiment analyzer with more nuance."""
    positive_words = ["love", "great", "good", "awesome", "amazing", "fantastic", "excellent"]
    negative_words = ["hate", "bad", "terrible", "awful", "boring", "annoying", "disappointing", "interrupting"]

    text_lower = text.lower()
    pos_score = sum(text_lower.count(w) for w in positive_words)
    neg_score = sum(text_lower.count(w) for w in negative_words)

    if pos_score > neg_score:
        sentiment = "positive"
    elif neg_score > pos_score:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "model": "sentiment_analysis",
        "sentiment": sentiment,
        "scores": {"positive": pos_score, "negative": neg_score}
    }
