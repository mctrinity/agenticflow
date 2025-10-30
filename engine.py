import json
from models import llama_guard_moderate, contentguard_score, sentiment_analysis
from logger import log_decision


MODEL_REGISTRY = {
    "llama_guard_3": llama_guard_moderate,
    "contentguard": contentguard_score,
    "sentiment_analysis": sentiment_analysis,
}

def run_pipeline(pipeline_path, input_text):
    with open(pipeline_path) as f:
        pipeline = json.load(f)

    context = {"text": input_text, "results": {}}

    for step in pipeline["steps"]:
        model_name = step["model"]
        func = MODEL_REGISTRY[model_name]

        print(f"\n[Running step: {step['id']}] → {model_name}")
        result = func(context["text"])
        context["results"][step["id"]] = result

        # Allow models to modify text dynamically
        if "modified_text" in result:
            context["text"] = result["modified_text"]

        # Don't break, just note unsafe flag
        if "unsafe" in result and result["unsafe"]:
            print("⚠️ Unsafe content detected — continuing in audit mode.")
            context["unsafe_detected"] = True

    # 🧠 Decision Policy Layer
    moderation = context["results"].get("moderation", {})
    civility = context["results"].get("civility", {}).get("civility_score", 1.0)
    sentiment = context["results"].get("sentiment", {}).get("sentiment", "neutral")

    if moderation.get("unsafe", False):
        decision = "block"
    elif civility < 0.8 or sentiment == "negative":
        decision = "review"
    else:
        decision = "allow"

    context["decision"] = decision

    # Log results to audit file
    log_decision(context)

    return context

