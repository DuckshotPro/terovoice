# /// script
# dependencies = [
#   "requests",
# ]
# ///

import requests
import json
import uuid
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000/api/auth"

def test_auth_flow():
    # 1. Generate unique user
    random_id = str(uuid.uuid4())[:8]
    email = f"test_{random_id}@example.com"
    password = "TestPassword123!"
    name = f"Test User {random_id}"

    print(f"Testing with: {email}")

    # 2. Test Registration
    print("\n1. Testing Registration...")
    try:
        reg_resp = requests.post(f"{BASE_URL}/register", json={
            "email": email,
            "password": password,
            "name": name
        })

        if reg_resp.status_code == 201:
            print("[OK] Registration Successful")
            print(f"Response: {reg_resp.json()}")
        else:
            print(f"[FAIL] Registration Failed: {reg_resp.status_code}")
            print(f"Error: {reg_resp.text}")
            return
    except requests.exceptions.ConnectionError:
        print("[FAIL] Could not connect to backend. Is it running on port 8000?")
        return

    # 3. Test Login
    print("\n2. Testing Login...")
    login_resp = requests.post(f"{BASE_URL}/login", json={
        "email": email,
        "password": password
    })

    if login_resp.status_code == 200:
        print("[OK] Login Successful")
        data = login_resp.json()
        token = data.get('token')
        if token:
            print("[OK] Token received")
        else:
            print(f"[FAIL] No token in response: {data}")
    else:
        print(f"[FAIL] Login Failed: {login_resp.status_code}")
        print(f"Error: {login_resp.text}")

if __name__ == "__main__":
    test_auth_flow()
