from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend-modern"

app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend-modern")

@app.get("/api/health")
def health():
    return {"status": "ok", "ui": "NAYALABEL AI modern frontend"}
