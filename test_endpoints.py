"""
Unit and integration test verification script for NyayaLabel AI backend & frontend.
"""
from starlette.testclient import TestClient
from backend.main import app

def run_tests():
    client = TestClient(app)
    
    print("1. Testing GET /api/analytics/dashboard...")
    r = client.get("/api/analytics/dashboard")
    assert r.status_code == 200, f"Dashboard failed: {r.status_code}"
    data = r.json()
    assert data["passed_count"] == 6, f"Expected 6 passed, got {data['passed_count']}"
    assert data["failed_count"] == 8, f"Expected 8 failed, got {data['failed_count']}"
    assert data["highest_risk"] == "0.93", f"Expected 0.93 risk, got {data['highest_risk']}"
    assert data["registered_companies"] == 8, f"Expected 8 companies, got {data['registered_companies']}"
    print("   [OK] Dashboard verified: Passed=6, Failed=8, Risk=0.93, Companies=8")

    print("2. Testing GET /api/products...")
    r = client.get("/api/products")
    assert r.status_code == 200
    assert r.json()["count"] >= 8
    print(f"   [OK] Products catalog verified: {r.json()['count']} products available")

    print("3. Testing GET /api/companies...")
    r = client.get("/api/companies")
    assert r.status_code == 200
    print(f"   [OK] FMCG companies verified: {r.json()['count']} companies registered")

    print("4. Testing GET /api/history...")
    r = client.get("/api/history")
    assert r.status_code == 200
    assert r.json()["count"] >= 14
    first_item = r.json()["items"][0]
    assert first_item["display_id"] == "#14"
    assert first_item["product_name"] == "Kurkure Schezwan"
    assert first_item["status"] == "Failed"
    assert first_item["risk_score"] == "0.93"
    print("   [OK] History verified: item #14 matches screenshot (Failed, 0.93 risk)")

    print("5. Testing GET / (Frontend mount)...")
    r = client.get("/")
    assert r.status_code == 200
    assert "NyayaLabel AI" in r.text
    assert "Live Packaging Label Scanner" in r.text
    assert "Compliance Protocol" in r.text
    print("   [OK] Frontend index.html served properly with all UI components")

    print("6. Testing GET /api/scan/NYAYA-2026-0014/pdf...")
    r = client.get("/api/scan/NYAYA-2026-0014/pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert len(r.content) > 1000
    print(f"   [OK] Statutory PDF report downloaded: {len(r.content)} bytes")

    print("7. Testing POST /api/auth/login & GET /api/auth/me...")
    login_res = client.post("/api/auth/login", json={"username": "officer", "password": "officer123"})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    assert "token-" in token
    assert login_res.json()["user"]["badge_number"] == "LMO-DL-7729"

    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["user"]["username"] == "officer"
    print("   [OK] Authentication verified: login, bearer token issuance, and profile resolution")

    print("\nALL BACKEND & FRONTEND INTEGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
