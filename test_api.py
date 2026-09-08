import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_flow():
    print("--- 1. Testing Root and Health ---")
    r = client.get("/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print("[PASS] Health check OK")

    print("\n--- 2. Testing Login as Admin ---")
    r = client.post("/api/auth/login", json={"login_id": "1001", "password": "admin123"})
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    admin_token = r.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[PASS] Admin login OK, token received")

    print("\n--- 3. Testing Login as Trabajador ---")
    r = client.post("/api/auth/login", json={"login_id": "2001", "password": "trabajador123"})
    assert r.status_code == 200, f"Worker login failed: {r.text}"
    worker_token = r.json()["access_token"]
    worker_headers = {"Authorization": f"Bearer {worker_token}"}
    print("[PASS] Trabajador login OK, token received")

    print("\n--- 4. Testing Login as Cliente with Email ---")
    r = client.post("/api/auth/login", json={"login_id": "atelier@maison.com", "password": "cliente123"})
    assert r.status_code == 200, f"Client login failed: {r.text}"
    client_token = r.json()["access_token"]
    client_headers = {"Authorization": f"Bearer {client_token}"}
    print("[PASS] Cliente login OK with email")

    print("\n--- 5. Testing Failed Login (Audit Logging) ---")
    r = client.post("/api/auth/login", json={"login_id": "1001", "password": "wrong_password"})
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    print("[PASS] Failed login rejected properly")

    print("\n--- 6. Testing Bitacora Access (RBAC) ---")
    # Admin can access bitacora
    r = client.get("/api/bitacora/", headers=admin_headers)
    assert r.status_code == 200, f"Admin failed to get bitacora: {r.text}"
    logs = r.json()
    assert len(logs) > 0, "Expected bitacora logs"
    print(f"[PASS] Admin retrieved {len(logs)} bitacora logs")

    # Worker can access bitacora
    r = client.get("/api/bitacora/", headers=worker_headers)
    assert r.status_code == 200, f"Worker failed to get bitacora: {r.text}"
    print("[PASS] Worker retrieved bitacora logs")

    # Client CANNOT access bitacora (403 Forbidden)
    r = client.get("/api/bitacora/", headers=client_headers)
    assert r.status_code == 403, f"Expected 403 Forbidden for Client, got {r.status_code}"
    print("[PASS] Client correctly denied access to Bitacora (403 Forbidden)")

    print("\n--- 7. Testing Forgot Password and Reset Password ---")
    r = client.post("/api/auth/forgot-password", json={"login_id": "atelier@maison.com"})
    assert r.status_code == 200, f"Forgot password failed: {r.text}"
    reset_token = r.json()["reset_token"]
    print("[PASS] Forgot password issued reset_token")

    r = client.post("/api/auth/reset-password", json={"reset_token": reset_token, "new_password": "cliente_new_123"})
    assert r.status_code == 200, f"Reset password failed: {r.text}"
    print("[PASS] Reset password updated successfully")

    # Login with new password
    r = client.post("/api/auth/login", json={"login_id": "atelier@maison.com", "password": "cliente_new_123"})
    assert r.status_code == 200, f"Login with new password failed: {r.text}"
    print("[PASS] Login with newly reset password confirmed")

    # Revert back to original password for testing consistency
    r = client.post("/api/auth/forgot-password", json={"login_id": "atelier@maison.com"})
    reset_token = r.json()["reset_token"]
    client.post("/api/auth/reset-password", json={"reset_token": reset_token, "new_password": "cliente123"})
    print("[PASS] Restored test client password")

    print("\n========================================")
    print("ALL 7 BACKEND TEST SCENARIOS PASSED 100%!")
    print("========================================")

if __name__ == "__main__":
    test_flow()
