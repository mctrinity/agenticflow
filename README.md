# 🤖 AgenticFlow Moderation Dashboard

An interactive FastAPI-based web dashboard for testing and visualizing AI-driven **content moderation pipelines**. It supports multiple moderation outcomes (✅ Allow, ⚠️ Warn, 🕵️ Review, ⛔ Block, 🧾 Escalate), automatic daily logging, and live summary updates.

---

## 🚀 Features

* **FastAPI + Jinja2 UI** — lightweight and reactive web interface.
* **Live Moderation Pipeline** — runs text through multi-model moderation (e.g., LlamaGuard, ContentGuard, sentiment analysis).
* **Automatic Logging** — JSONL audit logs with per-day summaries.
* **Auto-updating Dashboard** — live stats refresh every 10 seconds.
* **CSV Summary Generation** — each moderation decision updates `summary.csv`.
* **Warn & Escalate support** — extended moderation categories.
* **Simple UI Actions** — includes demo inputs and a Clear button.

---

## 🧩 Tech Stack

| Component                  | Purpose                           |
| -------------------------- | --------------------------------- |
| **FastAPI**                | Web server and routing            |
| **Jinja2**                 | HTML templating engine            |
| **pandas**                 | CSV and summary aggregation       |
| **JavaScript (vanilla)**   | Live updates and interactions     |
| **CSS (static/style.css)** | Modern, minimal dashboard styling |

---

## 🛠️ Installation

```bash
# Clone the repository
 git clone https://github.com/yourusername/AgenticFlow.git
 cd AgenticFlow

# Create a virtual environment
 python -m venv venv
 source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
 pip install -r requirements.txt

# Run the app
 uvicorn app:app --reload
```

Then open your browser to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 💡 Usage

### 1. Try Demo Inputs

Use the built-in buttons to auto-fill example moderation cases:

* ✅ **Allow** — safe, civil text
* ⚠️ **Warn** — mild profanity or tone issues
* 🕵️ **Review** — borderline civility or unclear tone
* ⛔ **Block** — unsafe or hateful content
* 🧾 **Escalate** — critical safety issue detected

### 2. Run Your Own Input

Enter any text in the input box and click **Run Moderation**.
The results will display inline, showing civility, sentiment, and moderation scores.

### 3. Clear Input

Click **Clear** to instantly wipe the textarea.

### 4. Live Summary

The summary section auto-refreshes every 10 seconds and displays:

* Total moderated texts today
* Count of each decision type
* Safe ratio
* Timestamp of last update

---

## 📁 Log Structure

Logs are stored per day under the `/logs/` directory:

```
logs/
 ├── 2025-10-31/
 │   ├── moderation_log.jsonl   # All moderation entries
 │   ├── summary.csv            # Daily summary statistics
 │   └── ...
```

The logger automatically compresses older logs into ZIP archives.

---

## ⚙️ Key Files

| File                   | Description                                                 |
| ---------------------- | ----------------------------------------------------------- |
| `app.py`               | FastAPI routes, moderation handling, and UI rendering       |
| `logger.py`            | Handles log writing, summary generation, and HTML rendering |
| `templates/index.html` | Main dashboard UI layout                                    |
| `static/style.css`     | Custom dashboard styling                                    |
| `static/script.js`     | Handles summary refresh and input clearing                  |
| `pipeline.json`        | Defines moderation pipeline configuration                   |

---

## 🧾 Example Output

```
Decision: REVIEW
Input: The host kept interrupting, and it got a bit annoying after a while.

Civility Score: 0.85
Sentiment: negative
Unsafe Detected: False
```

**📊 Summary Example:**

```
📊 Moderation Summary — 2025-10-31
Total: 7
✅ Allowed: 2
⚠️ Warned: 2
🕵️ Reviewed: 1
⛔ Blocked: 1
🧾 Escalated: 1
Safe Ratio: 0.29
⏱️ Last Updated: 09:42:10
```

---

## 🧰 Future Enhancements

* [ ] Add API endpoints for historical stats
* [ ] Enable filtering & search by decision type
* [ ] Add charts using Chart.js or Recharts
* [ ] Multi-user or team dashboards
* [ ] Integration with external moderation APIs

---

## 🧑‍💻 Author

**AgenticFlow Project** — AI-driven safety and content moderation tools.

---

### 🪪 License

MIT License — free to use, modify, and distribute.
