import os

tests_dir = "e:/ai/nyayalabel-ai/backend/tests"

with open(f"{tests_dir}/test_rules.py", "w", encoding="utf-8") as f:
    f.write('''import pytest
from app.services.rule_service import RuleService

def test_rule_definitions():
    service = RuleService()
    declarations = service.get_mandatory_declarations()
    assert len(declarations) >= 8
    rules_ids = [d["id"] for d in declarations]
    assert "RULE_6_1_A" in rules_ids
    assert "RULE_6_1_C" in rules_ids
    assert "RULE_6_1_E" in rules_ids
    assert "RULE_6_1_EA" in rules_ids

def test_prohibited_units():
    service = RuleService()
    val_table = service.get_validation_table()
    prohibited = val_table.get("prohibited_units", {})
    assert "gms" in prohibited
    assert "kgs" in prohibited
    assert "ml." in prohibited
''')

with open(f"{tests_dir}/test_inspections.py", "w", encoding="utf-8") as f:
    f.write('''from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["app"] == "NYAYALABEL AI"

def test_list_companies():
    res = client.get("/api/products/companies")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 10

def test_list_inspections():
    res = client.get("/api/inspections/")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) >= 2

def test_statutory_rules_endpoint():
    res = client.get("/api/rules/")
    assert res.status_code == 200
    data = res.json()
    assert "declarations" in data

def test_pdf_download():
    # Fetch first inspection
    res = client.get("/api/inspections/")
    scan_id = res.json()["items"][0]["scan_id"]
    res_pdf = client.get(f"/api/reports/{scan_id}/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert len(res_pdf.content) > 1000
''')

print("Created test_rules.py and test_inspections.py.")
