# 🤖 AgenticFlow

**AgenticFlow** is an *agentic moderation and governance system* that autonomously evaluates, scores, and decides how to handle user-generated content.
It uses a modular pipeline of AI reasoning models (moderation → civility → sentiment) to ensure safe, responsible, and brand-aligned interactions.

---

## 🧠 Overview

AgenticFlow isn't just a moderation tool — it's an **AI agent**.
It **observes**, **analyzes**, and **acts** — applying multi-model reasoning and policy rules to make contextual decisions such as:

* ✅ Allowing safe content
* 🕵️ Sending borderline cases for human review
* ⛔ Blocking unsafe or offensive material

Each moderation event is logged, summarized, and auditable — ensuring transparency and accountability.

---

## 🧱 Features

| Capability                    | Description                                                               |
| ----------------------------- | ------------------------------------------------------------------------- |
| 🧹 **Modular Pipeline**       | Chains multiple models dynamically (`moderation → civility → sentiment`). |
| 🧠 **Agentic Reasoning**      | Makes context-aware decisions (allow/review/block).                       |
| 📊 **Audit Logging**          | Saves every decision in JSONL format.                                     |
| 🗓️ **Daily Summaries**       | Generates `summary.csv` files per day automatically.                      |
| ⚖️ **Policy Rules**           | Decisions based on civility + sentiment thresholds.                       |
| 🧮 **Dynamic Input Chaining** | Each model’s output feeds into the next step.                             |
| �� **Transparency-First**     | All actions logged, summarized, and traceable.                            |

---

## ⚙️ Tech Stack

* **Language:** Python 3.11+
* **Core Libs:** `pandas`, `numpy`
* **Optional Enhancements:** `rich`, `fastapi`, `uvicorn`
* **Structure:** Modular (engine/models/logger)
* **Data Format:** JSON + JSONL for logs

---

## 🚀 Getting Started

### 1️⃣ Setup Environment

```bash
git clone https://github.com/yourusername/agenticflow.git
cd AgenticFlow
python -m venv venv
venv\Scripts\activate   # (on macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

### 2️⃣ Run the Pipeline

```bash
python run.py
```

### 3️⃣ Sample Output

```
[Running step: moderation] → llama_guard_3
[Running step: civility] → contentguard
[Running step: sentiment] → sentiment_analysis
🗒️ Logged decision → logs\2025-10-31\moderation_log.jsonl
📊 Today → 5 total | 4 ✅ allowed | 0 ⛔ blocked | 1 🕵️ reviewed | Safe Ratio: 0.8
```

---

## 🧮 Decision Policy

```python
if moderation.get("unsafe", False):
    decision = "block"
elif civility < 0.8 or sentiment == "negative":
    decision = "review"
else:
    decision = "allow"
```

### Outcomes

| Decision       | Meaning                              |
| -------------- | ------------------------------------ |
| ✅ **Allow**    | Safe and civil content               |
| 🕵️ **Review** | Borderline tone or mild negativity   |
| ⛔ **Block**    | Unsafe or explicitly harmful content |

---

## 🗂️ Folder Structure

```
AgenticFlow/
├── engine.py
├── models.py
├── logger.py
├── pipeline.json
├── run.py
├── requirements.txt
├── .gitignore
├── logs/
│   └── YYYY-MM-DD/
│       ├── moderation_log.jsonl
│       └── summary.csv
└── venv/
```

---

## 🦯 Roadmap

| Phase                     | Goal                                                    |
| ------------------------- | ------------------------------------------------------- |
| 1️⃣ **Weighted Scoring**  | Combine civility + sentiment into a unified risk index. |
| 2️⃣ **Policy Config**     | Externalize thresholds into a JSON config.              |
| 3️⃣ **API Agent**         | Serve moderation via REST (`/api/moderate`).            |
| 4️⃣ **Dashboard UI**      | Visualize logs and summaries in real time.              |
| 5️⃣ **Adaptive Learning** | Auto-tune civility and sentiment thresholds.            |

---

## 🦄 Example Input / Output

### Input

```text
The discussion was okay, but the guest kept interrupting and it was kind of annoying.
```

### Output

```json
{
  "text": "The discussion was okay, but the guest kept interrupting and it was kind of annoying.",
  "results": {
    "moderation": {"unsafe": false},
    "civility": {"civility_score": 0.87},
    "sentiment": {"sentiment": "negative"}
  },
  "decision": "review"
}
```

---

## 🧹 Credits

Created as a modular foundation for **agentic content safety systems** —
built to power responsible AI deployment, transparency, and compliance.

---

## �� License

MIT License © 2025 Maki Dizon
