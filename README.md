# NyayaLabel AI — Statutory Packaging Compliance Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)](https://fastapi.tiangolo.com/)
[![Legal Metrology](https://img.shields.io/badge/Legal%20Metrology-Act%202009%20%26%202026%20Rules-orange.svg)](https://consumeraffairs.nic.in/acts-and-rules/legal-metrology)
[![FSSAI](https://img.shields.io/badge/FSSAI-Statutory%20Format-red.svg)](https://www.fssai.gov.in/)

**NyayaLabel AI** is an automated compliance audit and enforcement engine designed for Indian packaged commodities under the **Legal Metrology Act, 2009**, the **Legal Metrology (Packaged Commodities) Rules, 2011 (Amended through 2026)**, and **FSSAI statutory packaging regulations**.

The system enables regulatory enforcement officers and FMCG brand managers to inspect product packaging labels via **file upload** or a **live browser webcam/camera scanner**, instantly auditing mandatory statutory declarations, computing compliance and risk scores, and generating official PDF inspection certificates.

---

## Key Features

1. **Exact Dark Theme Statutory Dashboard**
   - Inspection status breakdown bar (*Passed { 6 }*, *Failed { 8 }*, *Review Required { 0 }*).
   - Real-time tracking of *Highest Observed Risk* (`0.93`) and *Registered Companies* (`8`).
   - Recent inspections audit table with direct **Details** breakdown and **PDF Certificate** download.

2. **Live Camera Scanner with Target Reticle**
   - Direct integration with `navigator.mediaDevices.getUserMedia` for real-time mobile and desktop camera scanning.
   - Animated laser scan line, corner HUD targeting reticle, camera switcher (front/rear), and one-click snapshot capture.
   - Built-in synthetic test mock frame for headless or camera-less testing environments.

3. **6-Point Compliance Protocol Auditing**
   - **MRP Presence**: Currency symbol (₹), numeric price, and mandatory *"inclusive of all taxes"* clause (Rule 6(1)(e)).
   - **Net Quantity**: Standardized SI units (`g`, `kg`, `ml`, `l`, `N`), catching illegal non-standard units like `Gms.`, `gm`, `kgs` (Rule 6(1)(c) & Rule 12).
   - **Batch Identification**: Lot/batch code tracking audit (Rule 6(1)(g)).
   - **Mfg & Expiry Dates**: Date of packaging parsing and Best Before validity (Rule 6(1)(d)).
   - **Manufacturer & Origin**: Complete legal address verification with mandatory 6-digit Indian postal PIN code and Country of Origin (Rule 6(1)(a) & 6(1)(da)).
   - **FSSAI 14-Digit Format**: Statutory food safety license format validation.

4. **Official PDF Inspection Certificates**
   - Generates digitally formatted Legal Metrology inspection reports using ReportLab with officer notes, severity tags, and statutory notice recommendations under Section 36.

5. **Role-Based Authentication & Session Management**
   - Bearer token authentication with instant 1-click role switching.
   - Built-in pre-seeded accounts:
     - **Enforcement Officer**: `officer` / `officer123` (Badge `LMO-DL-7729`, R. K. Sharma)
     - **Brand Compliance Manager**: `manager` / `manager123` (Priya Patel, FMCG Quality)
     - **System Administrator**: `admin` / `admin123` (Director General)

---

## Quick Start: Local Run Guide

### Prerequisites
- **Python 3.10, 3.11, 3.12, or 3.13** — Download from [python.org](https://python.org).  
  > ⚠️ During installation, **check "Add Python to PATH"** — this is required for the startup scripts to work.
- **Modern web browser** — Chrome, Edge, or Firefox.

---

### ✅ Easiest Method: One-Click Startup (Windows)

**Double-click** [`start.bat`](./start.bat) in the project folder.

OR in PowerShell:
```powershell
cd E:\NAYALABELAI
.\start.ps1
```

Both scripts will automatically:
1. Create the Python virtual environment (if not already created)
2. Install all required packages from `backend/requirements.txt`
3. Start the server at `http://127.0.0.1:8000`

Then open your browser at **http://127.0.0.1:8000**

Login credentials:
| Role | Username | Password |
|------|----------|----------|
| Enforcement Officer | `officer` | `officer123` |
| Brand Manager | `manager` | `manager123` |
| Administrator | `admin` | `admin123` |

---

### Manual Method (If the script doesn't work)

#### Step 1 — Set Up Virtual Environment

Open PowerShell or CMD in the `E:\NAYALABELAI` folder:

```powershell
# Windows (PowerShell)
python -m venv backend\venv
.\backend\venv\Scripts\Activate.ps1
```

```cmd
# Windows (CMD / Command Prompt)
python -m venv backend\venv
backend\venv\Scripts\activate.bat
```

> **If you get `python not found`**: Install Python from https://python.org and make sure "Add to PATH" is checked.  
> **If you get a PowerShell execution policy error**: Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` first.

#### Step 2 — Install Dependencies

```bash
pip install -r backend/requirements.txt
```

#### Step 3 — Run the Local Server

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Step 4 — Open the App

Navigate to **http://127.0.0.1:8000** in your browser.

> The system automatically seeds **14 benchmark inspection records** (6 Passed, 8 Failed) on first run.

---

### Common Problems & Fixes

| Problem | Fix |
|---------|-----|
| `python` not found | Install Python 3.10+ and check "Add Python to PATH" |
| `Set-ExecutionPolicy` error in PowerShell | Run: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Port 8000 already in use | Change `--port 8000` to `--port 8001` in the command |
| Browser says "This site can't be reached" | Make sure the terminal/command window with uvicorn is still open |
| Camera not working | Use `http://127.0.0.1:8000` (not `localhost`) — browsers require this exact address for webcam |



## Using the Live Camera Inspection Feature

1. Navigate to **New Inspection** tab.
2. Under **Packaging Label Image**, click the **Use Camera** button.
3. Your browser will prompt: *"Allow 127.0.0.1 to use your camera?"* — Click **Allow**.
   > **Note on HTTPS/Localhost**: Browsers restrict webcam access (`getUserMedia`) to `localhost`, `127.0.0.1`, or HTTPS domains for security.
4. Position the packaged commodity label inside the holographic HUD reticle guidelines.
5. Click **Capture Snapshot** (or **Flip** to switch between front and rear cameras).
6. The snapshot will attach to the inspection form with an instant preview.
7. Click **Run AI Label Inspection** to execute the multi-pass statutory audit.

---

## Production Deployment Guide

### Option 1: Docker Deployment (Recommended)

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose port
EXPOSE 8000

# Start Uvicorn production server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Build and run with Docker:
```bash
docker build -t nyayalabel-ai .
docker run -d -p 8000:8000 --name nyayalabel nyayalabel-ai
```

---

### Option 2: Linux VM (Systemd Service + Nginx Reverse Proxy)

#### 1. Configure Systemd Service (`/etc/systemd/system/nyayalabel.service`):

```ini
[Unit]
Description=NyayaLabel AI Statutory Compliance Engine
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/nyayalabel
ExecStart=/var/www/nyayalabel/backend/venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable nyayalabel
sudo systemctl start nyayalabel
```

#### 2. Configure Nginx with SSL (Required for Live Webcam in Production):

```nginx
server {
    listen 80;
    server_name compliance.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name compliance.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/compliance.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/compliance.yourdomain.com/privkey.pem;

    client_max_body_size 25M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## API Documentation

Interactive OpenAPI / Swagger UI is available out of the box at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### Core Endpoints:
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/analytics/dashboard` | Returns summary metrics: `passed_count`, `failed_count`, `highest_risk`, and recent inspections. |
| `GET` | `/api/products` | Returns standard catalog of registered FMCG products with standard PDP dimensions. |
| `GET` | `/api/companies` | Returns registered FMCG manufacturers with registered PINs, FSSAI licenses, and helplines. |
| `GET` | `/api/history` | Returns searchable and filterable list of all historical inspections. |
| `POST` | `/api/scan/upload` | Uploads an image (multipart file or base64 webcam snapshot) and runs the compliance audit. |
| `GET` | `/api/scan/{scan_id}` | Retrieves full audit details for a specific inspection. |
| `GET` | `/api/scan/{scan_id}/pdf` | Generates and streams official PDF compliance report. |
| `GET` | `/api/scan/{scan_id}/json` | Exports full inspection data as downloadable JSON. |

---

## Statutory Legal References

- **The Legal Metrology Act, 2009** (Act No. 1 of 2010) — Section 36 (Penalty for manufacture, packing or sale of non-standard packaged commodities).
- **The Legal Metrology (Packaged Commodities) Rules, 2011** — Rule 6 (Declarations to be made on every package), Rule 7 & 8 (PDP and numeral height requirements), Rule 9 (Manner in which declaration shall be made), Rule 11 & 12 (Symbols for units).
- **Consumer Protection (E-Commerce) Rules & Legal Metrology 2021-2026 Amendments** — Unit Sale Price (USP) declarations and Country of Origin disclosures.
- **Food Safety and Standards (Packaging and Labelling) Regulations** — 14-digit FSSAI statutory license number format.

---

## License & Notice

Developed for statutory enforcement compliance and FMCG brand quality control.
All sample brands (*Kurkure*, *Amul*, *Britannia*, *Aashirvaad*, *Maggi*, *Parle-G*, *Tata Salt*, *Haldiram's*) are trademarks of their respective corporate owners used exclusively for statutory demonstration benchmarks.
