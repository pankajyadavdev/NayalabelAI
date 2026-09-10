import os

app_dir = "e:/ai/nyayalabel-ai/backend/app"

# 1. db/seed.py
with open(f"{app_dir}/db/seed.py", "w", encoding="utf-8") as f:
    f.write('''import json, os
from .database import SessionLocal, Base, engine
from ..models.product import FMCGCompanyDB
from ..models.inspection import InspectionDB
from ..config import FMCG_COMPANIES_FILE
from ..services.product_service import ProductService
from ..services.rule_service import RuleService
from ..services.compliance_service import ComplianceService

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed companies if empty
        if db.query(FMCGCompanyDB).count() == 0 and os.path.exists(FMCG_COMPANIES_FILE):
            with open(FMCG_COMPANIES_FILE, "r", encoding="utf-8") as f:
                comps = json.load(f)
            for c in comps:
                record = FMCGCompanyDB(
                    company_id=c["company_id"],
                    name=c["name"],
                    common_name=c.get("common_name", c["name"]),
                    brand_names_json=json.dumps(c.get("brand_names", [])),
                    registered_address=c.get("registered_address", ""),
                    pin_code=c.get("pin_code", ""),
                    city=c.get("city", ""),
                    state=c.get("state", ""),
                    fssai_lic_no=c.get("fssai_lic_no", ""),
                    consumer_care_json=json.dumps(c.get("consumer_care", {})),
                    categories_json=json.dumps(c.get("categories", []))
                )
                db.add(record)
            db.commit()
            print(f"Seeded {len(comps)} FMCG companies into database.")

        # Seed benchmark inspections if empty
        if db.query(InspectionDB).count() == 0:
            p_service = ProductService()
            r_service = RuleService()
            c_service = ComplianceService(p_service, r_service)

            # Sample 1: Aashirvaad Atta (Non-compliant unit 'Gms' & Font)
            atta_data = {
                "commodity_name": "Whole Wheat Shudh Chakki Atta",
                "brand_name": "Aashirvaad",
                "manufacturer_name_and_address": "ITC Limited, Virginia House, 37 J.L. Nehru Road, Kolkata - 700071, West Bengal",
                "net_quantity": "5000 Gms.",
                "date_of_manufacture": "08/2026",
                "best_before_expiry": "Best Before 4 Months",
                "mrp": "MRP ₹ 245.00 incl. of all taxes",
                "unit_sale_price": "₹ 49.00 / kg",
                "consumer_care": "ITC Consumer Care, Toll Free: 1800-425-44444, Email: itccares@itc.in",
                "country_of_origin": "India",
                "detected_font_height_mm": 2.1,
                "contrast_ratio": 5.2,
                "bounding_boxes": [
                    {"label": "Rule 6(1)(b) Generic Name", "text": "Aashirvaad Shudh Chakki Atta", "box": [80, 120, 480, 70], "status": "PASS"},
                    {"label": "Rule 6(1)(c) Net Qty (Violation)", "text": "Net Wt: 5000 Gms.", "box": [100, 240, 320, 50], "status": "FAIL"},
                    {"label": "Rule 6(1)(e) MRP & USP", "text": "MRP ₹ 245.00 incl. of all taxes | USP ₹ 49.00/kg", "box": [80, 340, 500, 60], "status": "PASS"},
                    {"label": "Rule 6(1)(a) Mfg Details & PIN", "text": "ITC Ltd, 37 J.L. Nehru Rd, Kolkata - 700071", "box": [80, 520, 560, 65], "status": "PASS"},
                    {"label": "Rule 6(1)(f) Consumer Care", "text": "Helpline: 1800-425-44444 | itccares@itc.in", "box": [80, 620, 520, 50], "status": "PASS"}
                ]
            }
            eval_atta = c_service.evaluate(atta_data, pdp_area_sq_cm=650.0)
            scan1 = InspectionDB(
                scan_id="NYAYA-2026-9041",
                product_name="Aashirvaad Shudh Chakki Atta 5kg",
                brand_name="Aashirvaad",
                company_name="ITC Limited (Foods Division)",
                image_filename="sample_aashirvaad_atta.jpg",
                pdp_area_sq_cm=650.0,
                overall_status=eval_atta["overall_status"],
                compliance_score=eval_atta["compliance_score"],
                violations_count=len(eval_atta["violations"]),
                extracted_declarations_json=json.dumps(atta_data),
                evaluation_result_json=json.dumps(eval_atta),
                officer_notes="Notice recommended under Section 36 for non-standard unit symbol 'Gms.'.",
                inspector_id="LMO-DL-7729"
            )
            db.add(scan1)

            # Sample 2: Amul Pasteurised Butter (Fully Compliant)
            butter_data = {
                "commodity_name": "Pasteurised Butter",
                "brand_name": "Amul",
                "manufacturer_name_and_address": "Gujarat Co-operative Milk Marketing Federation Ltd., Amul Dairy Road, Anand - 388001, Gujarat",
                "net_quantity": "500 g",
                "date_of_manufacture": "09/2026",
                "best_before_expiry": "Use by 12 months",
                "mrp": "MRP ₹ 275.00 (incl. of all taxes)",
                "unit_sale_price": "₹ 55.00 / 100 g",
                "consumer_care": "Amul Toll Free: 1800-258-3333, Email: customercare@amul.coop",
                "country_of_origin": "India",
                "detected_font_height_mm": 2.8,
                "contrast_ratio": 6.1,
                "bounding_boxes": [
                    {"label": "Rule 6(1)(b) Generic Name", "text": "Amul Pasteurised Butter", "box": [90, 80, 450, 70], "status": "PASS"},
                    {"label": "Rule 6(1)(c) Net Quantity", "text": "Net Weight: 500 g", "box": [90, 180, 280, 45], "status": "PASS"},
                    {"label": "Rule 6(1)(e) MRP Declaration", "text": "MRP ₹ 275.00 (incl. of all taxes)", "box": [90, 250, 460, 50], "status": "PASS"},
                    {"label": "Rule 6(1)(a) Mfg & PIN", "text": "GCMMF Ltd, Amul Dairy Rd, Anand - 388001", "box": [90, 450, 540, 60], "status": "PASS"},
                    {"label": "Rule 6(1)(f) Consumer Grievance", "text": "1800-258-3333 | customercare@amul.coop", "box": [90, 530, 500, 45], "status": "PASS"}
                ]
            }
            eval_butter = c_service.evaluate(butter_data, pdp_area_sq_cm=180.0)
            scan2 = InspectionDB(
                scan_id="NYAYA-2026-9038",
                product_name="Amul Pasteurised Butter 500g",
                brand_name="Amul",
                company_name="Gujarat Co-operative Milk Marketing Federation Ltd. (Amul)",
                image_filename="sample_amul_butter.jpg",
                pdp_area_sq_cm=180.0,
                overall_status=eval_butter["overall_status"],
                compliance_score=eval_butter["compliance_score"],
                violations_count=len(eval_butter["violations"]),
                extracted_declarations_json=json.dumps(butter_data),
                evaluation_result_json=json.dumps(eval_butter),
                officer_notes="Inspected and verified. All mandatory declarations conform to Legal Metrology Rules.",
                inspector_id="LMO-DL-7729"
            )
            db.add(scan2)
            db.commit()
            print("Seeded benchmark inspection scans into database.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
''')

# 2. main.py
with open(f"{app_dir}/main.py", "w", encoding="utf-8") as f:
    f.write('''import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import APP_NAME, APP_VERSION, BASE_DIR
from .db.database import Base, engine
from .db.seed import seed_database
from .api.inspections import router as inspections_router
from .api.products import router as products_router
from .api.rules import router as rules_router
from .api.reports import router as reports_router

# Initialize Database & Seed
Base.metadata.create_all(bind=engine)
seed_database()

app = FastAPI(
    title=APP_NAME,
    description="Automated Packaged Commodities Statutory Compliance System under Legal Metrology Act, 2009 & Packaged Commodities Rules 2011-2026",
    version=APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(inspections_router)
app.include_router(products_router)
app.include_router(rules_router)
app.include_router(reports_router)

# Health & Meta
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "app": APP_NAME, "version": APP_VERSION}

# Dashboard Analytics endpoint for frontend convenience
@app.get("/api/analytics/dashboard")
def get_dashboard_analytics():
    from .db.database import SessionLocal
    from .models.inspection import InspectionDB
    db = SessionLocal()
    try:
        scans = db.query(InspectionDB).all()
        total_scans = len(scans)
        compliant_count = sum(1 for s in scans if s.overall_status == "FULLY_COMPLIANT")
        non_compliant_count = sum(1 for s in scans if s.overall_status == "NON_COMPLIANT")
        review_count = sum(1 for s in scans if s.overall_status == "NEEDS_OFFICER_REVIEW")
        compliance_rate = round((compliant_count / total_scans * 100), 1) if total_scans > 0 else 100.0
        recent = [s.to_dict() for s in sorted(scans, key=lambda x: x.created_at, reverse=True)[:6]]

        return {
            "total_inspected": total_scans,
            "compliance_rate": compliance_rate,
            "compliant_count": compliant_count,
            "non_compliant_count": non_compliant_count,
            "review_count": review_count,
            "recent_activity": recent,
            "frequent_violations": [
                {"category": "Rule 6(1)(c) Non-Standard Units ('gms')", "count": 142},
                {"category": "Rule 6(1)(e) Missing 'incl. of all taxes'", "count": 98},
                {"category": "Rule 6(1)(a) Address Lacks 6-digit PIN", "count": 76},
                {"category": "Rule 6(1)(ea) Unit Sale Price (USP) Missing", "count": 65},
                {"category": "Rule 7 & 8 Font Height Below Threshold", "count": 51},
                {"category": "Rule 6(1)(f) Grievance Email / Phone Absent", "count": 32}
            ]
        }
    finally:
        db.close()

# Mount frontend
frontend_dir = os.path.join(BASE_DIR, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
''')

# 3. requirements.txt
with open("e:/ai/nyayalabel-ai/backend/requirements.txt", "w", encoding="utf-8") as f:
    f.write('''fastapi>=0.110.0
uvicorn>=0.28.0
pydantic>=2.6.0
sqlalchemy>=2.0.0
reportlab>=4.0.0
pillow>=10.0.0
pyyaml>=6.0.0
python-multipart>=0.0.9
requests>=2.31.0
pytest>=8.0.0
''')

print("Created seed.py, main.py, and requirements.txt.")
