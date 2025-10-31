import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import os
import csv
import shutil


# ----------------------------
# 🧠 Main Logger
# ----------------------------
def log_decision(context: dict):
    """Appends moderation results and decision to a daily audit log file."""

    # Create base log folder
    base_log_dir = Path("logs")
    base_log_dir.mkdir(exist_ok=True)

    # Create subfolder for today's date
    today = datetime.utcnow().strftime("%Y-%m-%d")
    daily_folder = base_log_dir / today
    daily_folder.mkdir(exist_ok=True)

    # Log file path
    log_file = daily_folder / "moderation_log.jsonl"

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "text": context.get("text"),
        "results": context.get("results", {}),
        "decision": context.get("decision"),
        "unsafe_detected": context.get("unsafe_detected", False)
    }

    # Append record to JSONL
    with open(log_file, "a", encoding="utf-8") as f:
        json.dump(record, f)
        f.write("\n")

    print(f"🗒️ Logged decision → {log_file}")

    # Generate / update summary CSV
    summary = update_daily_summary(daily_folder)

    # Console summary
    print(
        f"📊 Today → {summary['total']} total | "
        f"{summary['allowed']} ✅ allowed | "
        f"{summary['warned']} ⚠️ warned | "
        f"{summary['reviewed']} 🕵️ reviewed | "
        f"{summary['blocked']} ⛔ blocked | "
        f"{summary['escalated']} 🧾 escalated | "
        f"Safe Ratio: {summary['safe_ratio']}"
    )


# ----------------------------
# 📈 Daily Summary Updater
# ----------------------------
def update_daily_summary(daily_folder: Path):
    """Reads all logs from the day and generates or updates summary.csv."""
    log_file = daily_folder / "moderation_log.jsonl"
    summary_file = daily_folder / "summary.csv"

    if not log_file.exists():
        return {"total": 0, "allowed": 0, "warned": 0, "reviewed": 0, "blocked": 0, "escalated": 0, "safe_ratio": 0.0}

    # Load all decisions
    records = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not records:
        return {"total": 0, "allowed": 0, "warned": 0, "reviewed": 0, "blocked": 0, "escalated": 0, "safe_ratio": 0.0}

    df = pd.DataFrame(records)
    total = len(df)

    allowed = (df["decision"] == "allow").sum()
    warned = (df["decision"] == "warn").sum()
    reviewed = (df["decision"] == "review").sum()
    blocked = (df["decision"] == "block").sum()
    escalated = (df["decision"] == "escalate").sum()

    summary = {
        "date": daily_folder.name,
        "total": total,
        "allowed": allowed,
        "warned": warned,
        "reviewed": reviewed,
        "blocked": blocked,
        "escalated": escalated,
        "safe_ratio": round(allowed / total, 2) if total else 0,
    }

    # ✅ Write or append without overwriting history
    write_header = not summary_file.exists()
    with open(summary_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=summary.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(summary)

    return summary


# ----------------------------
# 📦 Archive older logs
# ----------------------------
def compress_old_logs():
    """Compresses log folders older than today into .zip for storage efficiency."""
    base_log_dir = Path("logs")
    today = datetime.utcnow().strftime("%Y-%m-%d")

    for folder in base_log_dir.iterdir():
        if folder.is_dir() and folder.name < today:
            zip_path = base_log_dir / f"{folder.name}.zip"
            if not zip_path.exists():
                shutil.make_archive(str(zip_path).replace(".zip", ""), "zip", folder)
                print(f"📦 Compressed logs → {zip_path}")


# ----------------------------
# 🧾 Summary HTML generator
# ----------------------------
def generate_summary_html():
    """Reads today's summary.csv and returns formatted HTML."""
    today = datetime.now().strftime("%Y-%m-%d")
    summary_path = os.path.join("logs", today, "summary.csv")

    print(f"📂 Looking for summary file: {summary_path}")  # helpful debug print

    # If no summary yet
    if not os.path.exists(summary_path):
        return """
        <div class="summary">
            <p>No moderation activity yet today.</p>
        </div>
        """

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except Exception as e:
        return f"<div class='summary'><p>Error reading summary: {e}</p></div>"

    if not data:
        return """
        <div class="summary">
            <p>No moderation activity yet today.</p>
        </div>
        """

    latest = data[-1]
    date = latest["date"]
    total = int(latest["total"])
    allowed = int(latest.get("allowed", 0))
    warned = int(latest.get("warned", 0))
    reviewed = int(latest.get("reviewed", 0))
    blocked = int(latest.get("blocked", 0))
    escalated = int(latest.get("escalated", 0))
    safe_ratio = float(latest.get("safe_ratio", 0))

    # Add local time for clarity
    last_updated = datetime.now().strftime("%H:%M:%S")

    return f"""
    <div class="summary fade-in">
        <h2>📊 Moderation Summary — {date}</h2>
        <ul>
            <li><b>Total:</b> {total}</li>
            <li><b>Allowed:</b> ✅ {allowed}</li>
            <li><b>Warned:</b> ⚠️ {warned}</li>
            <li><b>Reviewed:</b> 🕵️ {reviewed}</li>
            <li><b>Blocked:</b> ⛔ {blocked}</li>
            <li><b>Escalated:</b> 🧾 {escalated}</li>
            <li><b>Safe Ratio:</b> {safe_ratio:.2f}</li>
        </ul>
        <p style="font-size:13px; color:#888; margin-top:10px;">
            ⏱️ Last Updated: {last_updated}
        </p>
    </div>
    """
