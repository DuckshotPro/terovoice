
import socket
import urllib.request
import json
import sys

def check_port(host, port, service_name):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f"✅ {service_name} is OPEN on {host}:{port}")
            return True
        else:
            print(f"❌ {service_name} is CLOSED on {host}:{port}")
            return False
    except Exception as e:
        print(f"❌ {service_name} error: {e}")
        return False

def check_http(url, service_name):
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            print(f"✅ {service_name} HTTP Response: {response.getcode()} (URL: {url})")
            return True
    except Exception as e:
        print(f"❌ {service_name} HTTP Check Failed: {e}")
        return False

print("--- Checking Local Ecosystem ---")

# 1. Check Pieces OS
# Pieces often runs on 1000 (Linux/Mac) or 39300 (Windows)
pieces_found = False
if check_port("localhost", 1000, "Pieces OS (Port 1000)"):
    pieces_found = True
    check_http("http://localhost:1000/well-known/health", "Pieces OS Health")
    
if check_port("localhost", 39300, "Pieces OS (Port 39300)"):
    pieces_found = True
    check_http("http://localhost:39300/well-known/health", "Pieces OS Health")

# 2. Check n8n
if check_port("localhost", 5678, "n8n Automation"):
    check_http("http://localhost:5678/healthz", "n8n Health")

# 3. Check Neo4j
check_port("localhost", 7474, "Neo4j HTTP (Browser)")
check_port("localhost", 7687, "Neo4j Bolt")

if not pieces_found:
    print("\n⚠️  Pieces OS not detected. Is it running?")
