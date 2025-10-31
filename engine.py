import json
import re
from rich import print
from models import llama_guard_moderate, contentguard_score, sentiment_analysis
from logger import log_decision


MODEL_REGISTRY = {
    "llama_guard_3": llama_guard_moderate,
    "contentguard": contentguard_score,
    "sentiment_analysis": sentiment_analysis,
}


def decide(context):
    """Simplified moderation: allow, warn, or block."""
    mod = context["results"]["moderation"]
    civ = context["results"]["civility"]["civility_score"]
    sent = context["results"]["sentiment"]["sentiment"]
    text = context["text"].lower()

    # 1️⃣ Unsafe → block
    if mod.get("unsafe"):
        categories = [k for k, v in mod.get("categories", {}).items() if v]
        reason = ", ".join(categories) if categories else "unspecified"
        print(f"[bold red]⛔ Block:[/bold red] unsafe content detected ({reason}).")
        return "block"

    # 2️⃣ Profanity
    mild_profanity = re.findall(r"\b(hell|damn|crap|stupid|idiot|sucks)\b", text)
    severe_profanity = re.findall(r"\b(fuck|shit|bitch|asshole|bastard)\b", text)

    if severe_profanity:
        print("[bold red]⛔ Block:[/bold red] severe profanity detected.")
        return "block"

    if mild_profanity:
        print("[bold yellow]⚠️ Warn:[/bold yellow] mild profanity detected.")
        return "warn"

    # 3️⃣ Tone & civility
    if civ < 0.6:
        print("[bold red]⛔ Block:[/bold red] very low civility score.")
        return "block"

    if sent == "negative" and civ < 0.85:
        print("[bold yellow]⚠️ Warn:[/bold yellow] negative tone detected.")
        return "warn"

    # 4️⃣ Default: allow
    print("[bold green]✅ Allow:[/bold green] clean and civil.")
    return "allow"


def run_pipeline(pipeline_path, input_text):
    """Runs all models sequentially and logs the decision."""
    with open(pipeline_path) as f:
        pipeline = json.load(f)

    context = {"text": input_text, "results": {}}

    for step in pipeline["steps"]:
        model_name = step["model"]
        func = MODEL_REGISTRY[model_name]

        print(f"\n[Running step: {step['id']}] → {model_name}")
        result = func(context["text"])
        context["results"][step["id"]] = result

        # Dynamic chaining
        if "modified_text" in result:
            context["text"] = result["modified_text"]

        # Unsafe tracking
        if "unsafe" in result and result["unsafe"]:
            print("⚠️ Unsafe content detected — continuing in audit mode.")
            context["unsafe_detected"] = True

    # Decision & logging
    context["decision"] = decide(context)
    context["moderation_engine"] = pipeline["steps"][0]["model"]
    log_decision(context)

    return context
