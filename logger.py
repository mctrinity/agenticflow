import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import os
import csv
import shutil


def log_decision(context: dict):
    """Append moderation result and decision to a daily log."""
    base_log_dir = Path("logs")
    base_log_dir.mkdir(exist_ok=True)

    today = datetime.utcnow().strftime("%Y-%m-%d")
    daily_folder = base_log_dir / today
    daily_folder.mkdir(exist_ok=True)

    log_file = daily_folder / "moderation_log.jsonl"

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "text": context.get("text"),
        "results": context.get("results", {}),
        "decision": context.get("decision"),
        "unsafe_detected": context.get("unsafe_detected", False),
        "moderation_engine": context.get("moderation_engine", "unknown")
    }

    with open(log_file, "a", encoding="utf-8") as f:
        json.dump(record, f)
        f.write("\n")

    print(f"🗒️ Logged decision → {log_file}")

    # Update summary
    summary = update_daily_summary(daily_folder)
    print(
        f"📊 Today → {summary['total']} total | "
        f"{summary['allowed']} ✅ allowed | "
        f"{summary['warned']} ⚠️ warned | "
        f"{summary['blocked']} ⛔ blocked | "
        f"Safe Ratio: {summary['safe_ratio']} | "
        f"Engine: {summary['engine']}"
    )


def update_daily_summary(daily_folder: Path):
    """Generate today's moderation summary."""
    log_file = daily_folder / "moderation_log.jsonl"
    summary_file = daily_folder / "summary.csv"

    if not log_file.exists():
        return {"total": 0, "allowed": 0, "warned": 0, "blocked": 0, "safe_ratio": 0.0, "engine": "unknown"}

    records = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not records:
        return {"total": 0, "allowed": 0, "warned": 0, "blocked": 0, "safe_ratio": 0.0, "engine": "unknown"}

    df = pd.DataFrame(records)
    total = len(df)
    allowed = (df["decision"] == "allow").sum()
    warned = (df["decision"] == "warn").sum()
    blocked = (df["decision"] == "block").sum()

    summary = {
        "date": daily_folder.name,
        "total": total,
        "allowed": allowed,
        "warned": warned,
        "blocked": blocked,
        "safe_ratio": round(allowed / total, 2) if total else 0,
        "engine": df.get("moderation_engine", pd.Series(["unknown"])).iloc[-1],
    }

    pd.DataFrame([summary]).to_csv(summary_file, index=False)
    return summary


def generate_summary_html():
    """Render today's moderation summary as HTML."""
    today = datetime.now().strftime("%Y-%m-%d")
    summary_path = os.path.join("logs", today, "summary.csv")

    if not os.path.exists(summary_path):
        return "<div class='summary'><p>No moderation activity yet today.</p></div>"

    try:
        df = pd.read_csv(summary_path)
    except Exception as e:
        return f"<div class='summary'><p>Error reading summary: {e}</p></div>"

    if df.empty:
        return "<div class='summary'><p>No moderation activity yet today.</p></div>"

    latest = df.iloc[-1]
    date = latest['date']
    total = int(latest['total'])
    allowed = int(latest['allowed'])
    warned = int(latest['warned'])
    blocked = int(latest['blocked'])
    safe_ratio = float(latest['safe_ratio'])
    engine = latest.get('engine', 'unknown')
    last_updated = datetime.now().strftime("%H:%M:%S")

    return f"""
    <div class="summary fade-in">
        <h2>📊 Moderation Summary — {date}</h2>
        <ul>
            <li><b>Total:</b> {total}</li>
            <li><b>Allowed:</b> ✅ {allowed}</li>
            <li><b>Warned:</b> ⚠️ {warned}</li>
            <li><b>Blocked:</b> ⛔ {blocked}</li>
            <li><b>Safe Ratio:</b> {safe_ratio:.2f}</li>
            <li><b>Engine:</b> 🦙 {engine}</li>
        </ul>
        <p style="font-size:13px; color:#888; margin-top:10px;">
            ⏱️ Last Updated: {last_updated}
        </p>
    </div>
    """
