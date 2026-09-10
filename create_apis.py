import os

api_dir = "e:/ai/nyayalabel-ai/backend/app/api"
os.makedirs(api_dir, exist_ok=True)

# 1. rules.py
with open(f"{api_dir}/rules.py", "w", encoding="utf-8") as f:
    f.write('''from fastapi import APIRouter
from ..services.rule_service import RuleService

router = APIRouter(prefix="/api/rules", tags=["Statutory Rules"])
rule_service = RuleService()

@router.get("/")
def get_rules_summary():
    return {
        "general": rule_service.get_general_statutory_info(),
        "declarations": rule_service.get_mandatory_declarations(),
        "validation_tables": rule_service.get_validation_table()
    }

@router.get("/declarations")
def get_mandatory_declarations():
    return rule_service.get_mandatory_declarations()
''')

# 2. products.py
with open(f"{api_dir}/products.py", "w", encoding="utf-8") as f:
    f.write('''from fastapi import APIRouter, Query
from typing import Optional
from ..services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["FMCG Products & Companies"])
product_service = ProductService()

@router.get("/companies")
def list_companies(q: Optional[str] = Query(None)):
    companies = product_service.list_companies(query=q)
    return {"count": len(companies), "companies": companies}

@router.get("/")
def list_products():
    return {"message": "Product registry active", "count": len(product_service.list_companies())}
''')

# 3. reports.py
with open(f"{api_dir}/reports.py", "w", encoding="utf-8") as f:
    f.write('''import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..models.inspection import InspectionDB
from ..services.report_service import ReportService
from ..config import REPORTS_DIR

router = APIRouter(prefix="/api/reports", tags=["Inspection Reports"])
report_service = ReportService()

@router.get("/{scan_id}/pdf")
def download_pdf_report(scan_id: str, db: Session = Depends(get_db)):
    scan = db.query(InspectionDB).filter(InspectionDB.scan_id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Inspection scan not found.")
    
    pdf_path = os.path.join(REPORTS_DIR, f"NYAYALABEL_{scan_id}.pdf")
    report_service.generate_pdf(scan.to_dict(), pdf_path)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"NYAYALABEL_Inspection_Report_{scan_id}.pdf"
    )

@router.get("/{scan_id}/json")
def download_json_report(scan_id: str, db: Session = Depends(get_db)):
    scan = db.query(InspectionDB).filter(InspectionDB.scan_id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Inspection scan not found.")
    return JSONResponse(
        content=scan.to_dict(),
        headers={"Content-Disposition": f"attachment; filename=NYAYALABEL_{scan_id}.json"}
    )
''')

# 4. inspections.py
with open(f"{api_dir}/inspections.py", "w", encoding="utf-8") as f:
    f.write('''import os, json, uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..models.inspection import InspectionDB
from ..schemas.inspection import InspectionCreateRequest
from ..services.product_service import ProductService
from ..services.rule_service import RuleService
from ..services.ocr_service import OCRService
from ..services.vision_service import VisionService
from ..services.compliance_service import ComplianceService
from ..config import UPLOAD_DIR, DEFAULT_INSPECTOR_ID

router = APIRouter(prefix="/api/inspections", tags=["Inspection & Compliance Scans"])

product_service = ProductService()
rule_service = RuleService()
ocr_service = OCRService()
vision_service = VisionService()
compliance_service = ComplianceService(product_service, rule_service)

@router.get("/")
def list_inspections(
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(InspectionDB)
    if status and status != "ALL":
        query = query.filter(InspectionDB.overall_status == status)
    
    items = query.order_by(InspectionDB.created_at.desc()).all()
    results = [s.to_dict() for s in items]

    if q:
        q_lower = q.lower()
        results = [
            r for r in results
            if q_lower in r["product_name"].lower() or 
               q_lower in (r.get("company_name") or "").lower() or
               q_lower in (r.get("brand_name") or "").lower() or
               q_lower in r["scan_id"].lower()
        ]
    return {"count": len(results), "items": results}

@router.get("/{scan_id}")
def get_inspection_detail(scan_id: str, db: Session = Depends(get_db)):
    item = db.query(InspectionDB).filter(InspectionDB.scan_id == scan_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inspection scan record not found.")
    return item.to_dict()

@router.post("/upload")
async def upload_and_inspect(
    image: UploadFile = File(...),
    product_name: str = Form("Inspected Packaged Food Product"),
    pdp_area_sq_cm: float = Form(150.0),
    officer_notes: Optional[str] = Form(""),
    db: Session = Depends(get_db)
):
    scan_id = f"NYAYA-2026-{uuid.uuid4().hex[:6].upper()}"
    filename = f"{scan_id}_{image.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        content = await image.read()
        f.write(content)

    img_props = vision_service.analyze_image_properties(filepath)
    extracted = ocr_service.extract_label_data(filepath, filename_hint=image.filename)
    extracted["contrast_ratio"] = img_props["contrast_ratio"]

    matched = product_service.match_company(
        extracted.get("manufacturer_name_and_address", "") + " " + extracted.get("brand_name", "") + " " + product_name
    )
    company_name = matched.get("name") if matched else "Independent Indian Manufacturer"
    brand_name = extracted.get("brand_name") or product_name.split()[0]

    evaluation = compliance_service.evaluate(extracted, pdp_area_sq_cm=pdp_area_sq_cm)

    record = InspectionDB(
        scan_id=scan_id,
        product_name=product_name if product_name != "Inspected Packaged Food Product" else extracted.get("commodity_name", product_name),
        brand_name=brand_name,
        company_name=company_name,
        image_filename=filename,
        pdp_area_sq_cm=pdp_area_sq_cm,
        overall_status=evaluation["overall_status"],
        compliance_score=evaluation["compliance_score"],
        violations_count=len(evaluation["violations"]),
        extracted_declarations_json=json.dumps(extracted),
        evaluation_result_json=json.dumps(evaluation),
        officer_notes=officer_notes,
        inspector_id=DEFAULT_INSPECTOR_ID
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return record.to_dict()

@router.post("/evaluate")
def evaluate_digital_declarations(req: InspectionCreateRequest, db: Session = Depends(get_db)):
    scan_id = f"NYAYA-2026-{uuid.uuid4().hex[:6].upper()}"
    extracted = req.extracted_data.model_dump()

    matched = product_service.match_company(
        (extracted.get("manufacturer_name_and_address") or "") + " " + (extracted.get("brand_name") or "")
    )
    company_name = matched.get("name") if matched else "Registered Packer / Importer"
    brand_name = extracted.get("brand_name") or req.product_name.split()[0]

    evaluation = compliance_service.evaluate(extracted, pdp_area_sq_cm=req.pdp_area_sq_cm or 150.0)

    record = InspectionDB(
        scan_id=scan_id,
        product_name=req.product_name,
        brand_name=brand_name,
        company_name=company_name,
        image_filename=None,
        pdp_area_sq_cm=req.pdp_area_sq_cm or 150.0,
        overall_status=evaluation["overall_status"],
        compliance_score=evaluation["compliance_score"],
        violations_count=len(evaluation["violations"]),
        extracted_declarations_json=json.dumps(extracted),
        evaluation_result_json=json.dumps(evaluation),
        officer_notes=req.officer_notes or "Digital declaration verification against statutory rules.",
        inspector_id=DEFAULT_INSPECTOR_ID
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return record.to_dict()
''')

# 5. api/__init__.py
with open(f"{api_dir}/__init__.py", "w", encoding="utf-8") as f:
    f.write('''from .inspections import router as inspections_router
from .products import router as products_router
from .rules import router as rules_router
from .reports import router as reports_router

__all__ = ["inspections_router", "products_router", "rules_router", "reports_router"]
''')

print("Created all API routers successfully!")
