import json
import gzip
from datetime import datetime
from pathlib import Path
import pandas as pd  # Make sure pandas is installed: pip install pandas

def log_decision(context: dict):
    """Appends moderation results and decision to a daily audit log file."""

    # Create base log folder
    base_log_dir = Path("logs")
    base_log_dir.mkdir(exist_ok=True)

    # Create subfolder for today's date
    today = datetime.utcnow().strftime("%Y-%m-%d")
    daily_folder = base_log_dir / today
    daily_folder.mkdir(exist_ok=True)

    # Log file
    log_file = daily_folder / "moderation_log.jsonl"

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "text": context.get("text"),
        "results": context.get("results", {}),
        "decision": context.get("decision"),
        "unsafe_detected": context.get("unsafe_detected", False)
    }

    # Append record
    with open(log_file, "a", encoding="utf-8") as f:
        json.dump(record, f)
        f.write("\n")

    print(f"🗒️ Logged decision → {log_file}")

    # Generate summary after each entry
    summary = update_daily_summary(daily_folder)

    # Print friendly summary stats to console
    print(
        f"📊 Today → {summary['total']} total | "
        f"{summary['allowed']} ✅ allowed | "
        f"{summary['blocked']} ⛔ blocked | "
        f"{summary['reviewed']} 🕵️ reviewed | "
        f"Safe Ratio: {summary['safe_ratio']}"
    )


def update_daily_summary(daily_folder: Path):
    """Reads all logs from the day and generates a summary CSV."""
    log_file = daily_folder / "moderation_log.jsonl"
    summary_file = daily_folder / "summary.csv"

    records = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not records:
        return {"total": 0, "allowed": 0, "blocked": 0, "reviewed": 0, "safe_ratio": 0.0}

    df = pd.DataFrame(records)

    total = len(df)
    allowed = (df["decision"] == "allow").sum()
    blocked = (df["decision"] == "block").sum()
    reviewed = (df["decision"] == "review").sum()

    summary = {
        "date": daily_folder.name,
        "total": total,
        "allowed": allowed,
        "blocked": blocked,
        "reviewed": reviewed,
        "safe_ratio": round(allowed / total, 2) if total else 0,
    }

    # Write/overwrite daily summary file
    pd.DataFrame([summary]).to_csv(summary_file, index=False)

    return summary


def compress_old_logs():
    """Compresses log folders older than today into .zip for storage efficiency."""
    base_log_dir = Path("logs")
    today = datetime.utcnow().strftime("%Y-%m-%d")

    for folder in base_log_dir.iterdir():
        if folder.is_dir() and folder.name < today:
            zip_path = base_log_dir / f"{folder.name}.zip"
            if not zip_path.exists():
                import shutil
                shutil.make_archive(str(zip_path).replace(".zip", ""), 'zip', folder)
                print(f"📦 Compressed logs → {zip_path}")
