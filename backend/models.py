"""
Database and Pydantic models for Legal Metrology application.
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean
from datetime import datetime
import json
from .database import Base
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# SQLAlchemy DB Models
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(50), default="ENFORCEMENT_OFFICER") # ENFORCEMENT_OFFICER, BRAND_MANAGER, ADMIN
    full_name = Column(String(100))
    department = Column(String(100), default="Legal Metrology Directorate")
    badge_number = Column(String(50), default="LMO-DL-7729")
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "role": self.role,
            "department": self.department,
            "badge_number": self.badge_number,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class ProductScanDB(Base):
    __tablename__ = "product_scans"
    id = Column(Integer, primary_key=True, index=True)
    display_id = Column(String(20), nullable=True) # e.g. "#14", "#13"
    scan_id = Column(String(50), unique=True, index=True, nullable=False)
    product_name = Column(String(200), nullable=False)
    brand_name = Column(String(100), nullable=True)
    company_name = Column(String(200), nullable=True)
    image_filename = Column(String(255), nullable=True)
    pdp_area_sq_cm = Column(Float, default=150.0)
    overall_status = Column(String(50), nullable=False) # Passed, Failed, Review Required
    risk_score = Column(Float, default=0.0) # 0.93, 0.00, etc.
    compliance_score = Column(Integer, default=0)
    violations_count = Column(Integer, default=0)
    extracted_data_json = Column(Text, nullable=False)
    evaluation_result_json = Column(Text, nullable=False)
    officer_notes = Column(Text, nullable=True)
    inspector_id = Column(String(50), default="LMO-DL-7729")
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        ts_str = ""
        if self.created_at:
            h = self.created_at.strftime("%I").lstrip("0") or "12"
            ts_str = f"{self.created_at.month}/{self.created_at.day}/{self.created_at.year}, {h}:{self.created_at.strftime('%M:%S %p').lower()}"

        norm_status = self.overall_status
        if self.overall_status in ["FULLY_COMPLIANT", "COMPLIANT", "PASS", "Passed"]:
            norm_status = "Passed"
        elif self.overall_status in ["NON_COMPLIANT", "FAIL", "Failed"]:
            norm_status = "Failed"
        elif self.overall_status in ["NEEDS_OFFICER_REVIEW", "REVIEW_REQUIRED", "Review Required"]:
            norm_status = "Review Required"

        return {
            "id": self.id,
            "display_id": self.display_id or f"#{self.id}",
            "scan_id": self.scan_id,
            "product": self.product_name,
            "product_name": self.product_name,
            "brand_name": self.brand_name or "",
            "company_name": self.company_name or "",
            "image_filename": self.image_filename,
            "pdp_area_sq_cm": self.pdp_area_sq_cm,
            "status": norm_status,
            "overall_status": norm_status,
            "risk_score": f"{self.risk_score:.2f}" if self.risk_score is not None else "0.00",
            "compliance_score": self.compliance_score,
            "violations_count": self.violations_count,
            "extracted_data": json.loads(self.extracted_data_json) if self.extracted_data_json else {},
            "evaluation_result": json.loads(self.evaluation_result_json) if self.evaluation_result_json else {},
            "officer_notes": self.officer_notes,
            "inspector_id": self.inspector_id,
            "timestamp": ts_str,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# Pydantic Schemas
class ExtractedDataSchema(BaseModel):
    commodity_name: Optional[str] = None
    brand_name: Optional[str] = None
    manufacturer_name_and_address: Optional[str] = None
    net_quantity: Optional[str] = None
    date_of_manufacture: Optional[str] = None
    best_before_expiry: Optional[str] = None
    mrp: Optional[str] = None
    unit_sale_price: Optional[str] = None
    consumer_care: Optional[str] = None
    country_of_origin: Optional[str] = "India"
    fssai_license: Optional[str] = None
    batch_number: Optional[str] = None
    detected_font_height_mm: Optional[float] = 2.5
    contrast_ratio: Optional[float] = 4.5
    is_blow_moulded_container: Optional[bool] = False

class ScanRequestSchema(BaseModel):
    product_name: str
    pdp_area_sq_cm: Optional[float] = 150.0
    extracted_data: ExtractedDataSchema

class LoginRequest(BaseModel):
    username: str
    password: str