import json
import re
from rich import print  # for colorized logs
from models import llama_guard_moderate, contentguard_score, sentiment_analysis
from logger import log_decision


MODEL_REGISTRY = {
    "llama_guard_3": llama_guard_moderate,
    "contentguard": contentguard_score,
    "sentiment_analysis": sentiment_analysis,
}


def decide(context):
    """Smarter decision logic with nuanced thresholds."""
    mod = context["results"]["moderation"]
    civ = context["results"]["civility"]["civility_score"]
    sent = context["results"]["sentiment"]["sentiment"]
    text = context["text"].lower()

    # 🔒 1️⃣ Handle unsafe content categories
    if mod.get("unsafe"):
        if mod["categories"].get("violence") or mod["categories"].get("sexual"):
            print("[bold magenta]🧾 Escalate:[/bold magenta] critical safety category triggered.")
            return "escalate"
        print("[bold red]⛔ Block:[/bold red] unsafe content detected.")
        return "block"

    # 🧮 2️⃣ Profanity detection
    mild_profanity = re.findall(r"\b(hell|damn|crap|stupid|idiot|sucks)\b", text)
    severe_profanity = re.findall(r"\b(fuck|shit|bitch|asshole|bastard)\b", text)

    if severe_profanity:
        print("[bold red]⛔ Block:[/bold red] severe profanity detected.")
        return "block"

    if mild_profanity:
        print("[bold yellow]⚠️ Warn:[/bold yellow] mild profanity detected.")
        return "warn"

    # 🤝 3️⃣ Civility & sentiment thresholds
    if civ < 0.7:
        print("[bold yellow]🕵️ Review:[/bold yellow] civility too low.")
        return "review"

    if sent == "negative" and civ < 0.9:
        print("[bold yellow]🕵️ Review:[/bold yellow] negative tone with borderline civility.")
        return "review"

    # ✅ 4️⃣ Safe content
    print("[bold green]✅ Allow:[/bold green] clean and civil.")
    return "allow"


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

        # Dynamic input chaining
        if "modified_text" in result:
            context["text"] = result["modified_text"]

        # Unsafe audit tracking
        if "unsafe" in result and result["unsafe"]:
            print("⚠️ Unsafe content detected — continuing in audit mode.")
            context["unsafe_detected"] = True

    # 🧠 Decision Policy Layer
    context["decision"] = decide(context)

    # Log results to audit file
    log_decision(context)

    return context
