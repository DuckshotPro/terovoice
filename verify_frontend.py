# /// script
# dependencies = [
#   "requests",
# ]
# ///

import requests
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')

FRONTEND_URL = "http://localhost:5174"

def check_frontend():
    print(f"Checking Frontend at {FRONTEND_URL}...")
    try:
        resp = requests.get(FRONTEND_URL)
        if resp.status_code == 200:
            print("[OK] Frontend is accessible!")
            print(f"Title: {resp.text[:100]}...") # Print first 100 chars
        else:
            print(f"[FAIL] Frontend returned status {resp.status_code}")
    except requests.exceptions.ConnectionError:
        print("[FAIL] Could not connect to Frontend. Is it running?")

if __name__ == "__main__":
    check_frontend()
