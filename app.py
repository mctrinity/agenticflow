from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from engine import run_pipeline
from logger import generate_summary_html
import pandas as pd
import os
from datetime import datetime

app = FastAPI(title="AgenticFlow UI")

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load templates folder
templates = Jinja2Templates(directory="templates")


def get_today_summary():
    """Load today's summary CSV (if exists)."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join("logs", date_str, "summary.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        if not df.empty:
            row = df.iloc[-1]
            return {
                "date": row["date"],
                "total": int(row["total"]),
                "allowed": int(row["allowed"]),
                "blocked": int(row["blocked"]),
                "warned": int(row.get("warned", 0)),
                "safe_ratio": float(row["safe_ratio"]),
            }
    return None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page."""
    summary = get_today_summary()
    summary_html = generate_summary_html() if summary else "<div class='summary'><p>No moderation activity yet today.</p></div>"
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "summary_html": summary_html, "result_html": ""}
    )


@app.post("/moderate", response_class=HTMLResponse)
async def moderate(request: Request, text: str = Form(...)):
    """Run the moderation pipeline with input validation."""
    text = text.strip()

    # 🛑 Prevent empty submissions
    if not text:
        summary_html = generate_summary_html()
        result_html = """
        <div class="result" style="color: red; padding: 10px; border: 1px solid #f88; background: #fff3f3; border-radius: 8px;">
            ⚠️ Please enter text before running moderation.
        </div>
        """
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "summary_html": summary_html, "result_html": result_html}
        )

    # ✅ Run moderation pipeline
    result = run_pipeline("pipeline.json", text)
    decision = result["decision"].lower()
    civility = result["results"]["civility"]["civility_score"]
    sentiment = result["results"]["sentiment"]["sentiment"]
    unsafe = result["results"]["moderation"]["unsafe"]

    result_html = f"""
    <div class="result">
        <h2>Decision: <span class="badge {decision}">{decision.upper()}</span></h2>
        <p><b>Input:</b> {text}</p>
        <ul>
            <li><b>Civility Score:</b> {civility}</li>
            <li><b>Sentiment:</b> {sentiment}</li>
            <li><b>Unsafe Detected:</b> {unsafe}</li>
        </ul>
        <pre>{result}</pre>
        <a href="/">← Back</a>
    </div>
    """

    summary_html = generate_summary_html()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "summary_html": summary_html, "result_html": result_html}
    )


@app.get("/summary", response_class=HTMLResponse)
async def get_summary():
    """Return the rendered summary HTML snippet (for JS auto-refresh)."""
    return generate_summary_html()


@app.get("/moderate")
async def redirect_to_home():
    """Redirect manual /moderate GET requests to home."""
    return RedirectResponse(url="/")
