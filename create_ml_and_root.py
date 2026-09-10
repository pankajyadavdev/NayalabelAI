import os, shutil

base = "e:/ai/nyayalabel-ai"

# 1. ML Modules
os.makedirs(f"{base}/ml/ocr", exist_ok=True)
with open(f"{base}/ml/ocr/pipeline.py", "w", encoding="utf-8") as f:
    f.write('''"""
NYAYALABEL AI - OCR Pipeline.
Multi-stage text extraction for packaged commodities.
"""
from typing import Dict, Any

class OCRPipeline:
    def __init__(self):
        pass

    def run_ocr(self, image_path: str) -> Dict[str, Any]:
        return {"raw_text": "", "confidence": 0.95}
''')

os.makedirs(f"{base}/ml/font_analysis", exist_ok=True)
with open(f"{base}/ml/font_analysis/font_calculator.py", "w", encoding="utf-8") as f:
    f.write('''"""
NYAYALABEL AI - Font & Numeral Height Estimator.
Calculates letter/digit height in millimeters from DPI and bounding boxes.
"""
class FontCalculator:
    @staticmethod
    def estimate_height_mm(box_height_px: float, dpi: float = 300.0) -> float:
        # mm = (pixels / dpi) * 25.4
        return (box_height_px / dpi) * 25.4
''')

os.makedirs(f"{base}/ml/detection", exist_ok=True)
with open(f"{base}/ml/detection/box_detector.py", "w", encoding="utf-8") as f:
    f.write('''"""
NYAYALABEL AI - Bounding Box Localization for Mandatory Declarations.
"""
class BoxDetector:
    pass
''')

# 2. rules/packaged_commodities/README.md
with open(f"{base}/rules/packaged_commodities/README.md", "w", encoding="utf-8") as f:
    f.write('''# Legal Metrology (Packaged Commodities) Rules Repository

This directory contains the machine-readable YAML definitions for statutory compliance under the **Legal Metrology Act, 2009** and the **Legal Metrology (Packaged Commodities) Rules, 2011 (with amendments up to 2026)**.

### Subdirectories:
- 2026/general.yaml: Act citations, statutory portal link, and Section 36 penalty provisions.
- 2026/declarations.yaml: Mandatory declarations (Rules 6(1)(a)-(g), 6(10), 7, 8, 9).
- 2026/validation.yaml: Standard SI metric units, prohibited symbols, and PDP font height Table.
''')

# 3. docker-compose.yml
with open(f"{base}/docker-compose.yml", "w", encoding="utf-8") as f:
    f.write('''version: '3.8'

services:
  nyayalabel-api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: nyayalabel-ai
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:////app/data/nyayalabel.db
      - PYTHONUNBUFFERED=1
    volumes:
      - ./data:/app/data
    restart: unless-stopped
''')

# 4. .env
with open(f"{base}/.env", "w", encoding="utf-8") as f:
    f.write('''APP_NAME=NYAYALABEL AI
APP_ENV=production
DATABASE_URL=sqlite:///e:/ai/nyayalabel-ai/data/nyayalabel.db
PORT=8000
HOST=127.0.0.1
DEFAULT_INSPECTOR_ID=LMO-DL-7729
STATUTORY_PORTAL_URL=https://consumeraffairs.nic.in/acts-and-rules/legal-metrology
''')

# 5. README.md
with open(f"{base}/README.md", "w", encoding="utf-8") as f:
    f.write('''# NYAYALABEL AI ⚖️

**Automated Compliance & Enforcement System for Packaged Commodities**  
Under the **Legal Metrology Act, 2009** and the **Legal Metrology (Packaged Commodities) Rules, 2011 (Amended through 2026)**.

---

## 🏛️ Statutory Alignment
- **Governing Legislation**: Legal Metrology Act, 2009 (Act No. 1 of 2010)
- **Rules Enforced**: Legal Metrology (Packaged Commodities) Rules, 2011 to 2026
- **Department**: Directorate of Legal Metrology, Department of Consumer Affairs, Government of India
- **Official Portal**: [https://consumeraffairs.nic.in/acts-and-rules/legal-metrology](https://consumeraffairs.nic.in/acts-and-rules/legal-metrology)

---

## 📁 Repository Architecture

`
nyayalabel-ai/
│
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI Application Entrypoint
│   │   ├── config.py                 # App Configuration & Paths
│   │   ├── api/
│   │   │   ├── inspections.py        # Scan Upload & Compliance APIs
│   │   │   ├── products.py           # FMCG Companies & Catalog APIs
│   │   │   ├── rules.py              # Statutory Rules & Declarations
│   │   │   └── reports.py            # PDF & JSON Export APIs
│   │   ├── models/                   # SQLAlchemy DB Models
│   │   ├── schemas/                  # Pydantic Schemas
│   │   ├── services/                 # Compliance, OCR, Vision, Report Services
│   │   └── db/                       # Database Session & Seed Script
│   ├── tests/                        # Automated Test Suite
│   └── requirements.txt
│
├── ml/
│   ├── ocr/                          # OCR Extraction Pipeline
│   ├── detection/                    # Bounding Box Localization
│   ├── classification/               # Commodity Category Classifier
│   ├── font_analysis/                # Numeral & Font Height Calculator
│   └── datasets/                     # Packaging Label Benchmark Sets
│
├── rules/
│   └── packaged_commodities/2026/    # Machine-Readable YAML Statutory Rules
│
├── frontend/                         # Modern Interactive Enforcement Dashboard
├── data/                             # SQLite DB, Images, & FMCG Masters
├── docker-compose.yml
├── README.md
└── .env
`

---

## 🚀 Quick Start

### 1. Install Dependencies
`ash
cd nyayalabel-ai/backend
pip install -r requirements.txt
`

### 2. Run Database Seeding
`ash
python -m app.db.seed
`

### 3. Launch Application
`ash
uvicorn app.main:app --reload --port 8000
`
Open **http://127.0.0.1:8000** in your browser.
''')

# 6. Copy frontend files from e:\ai\frontend to e:\ai\nyayalabel-ai\frontend
shutil.copy("e:/ai/frontend/index.html", f"{base}/frontend/index.html")
shutil.copy("e:/ai/frontend/app.js", f"{base}/frontend/app.js")
shutil.copy("e:/ai/frontend/style.css", f"{base}/frontend/style.css")

# Update branding in index.html to NYAYALABEL AI
with open(f"{base}/frontend/index.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("LegalMetrologyScan", "NYAYALABEL<span class=\"text-amber-400\">AI</span>")
html = html.replace("Legal Metrology (Packaged Commodities) Compliance System", "NYAYALABEL AI — Legal Metrology Compliance System")

with open(f"{base}/frontend/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Created all ML stubs, rules README, docker-compose, README, .env, and updated NYAYALABEL AI frontend!")
