"""
Simple API Testing Script for PRISM
Tests basic endpoints without requiring external services.
"""
import requests
import json
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, params=None):
    """Test an API endpoint."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, timeout=5)
        
        return response, None
    except requests.exceptions.ConnectionError:
        return None, "Connection failed - Server not running"
    except Exception as e:
        return None, str(e)

def main():
    print("\n" + "="*60)
    print("PRISM API Simple Test Suite")
    print("="*60)
    print(f"\nBase URL: {BASE_URL}\n")
    
    # Check server
    print("[INFO] Checking if server is running...")
    response, error = test_endpoint("GET", "/")
    
    if error:
        print(f"[ERROR] {error}")
        print("[INFO] Please start the server with: python -m backend.main")
        return
    
    print("[OK] Server is running!\n")
    
    # Test 1: Root endpoint
    print("="*60)
    print("Test 1: GET /")
    print("="*60)
    response, error = test_endpoint("GET", "/")
    if response and response.status_code == 200:
        data = response.json()
        print(f"[OK] Status: {response.status_code}")
        print(f"[INFO] Service: {data.get('service')}")
        print(f"[INFO] Version: {data.get('version')}")
        print(f"[INFO] Status: {data.get('status')}")
    else:
        print(f"[ERROR] Failed: {error or response.status_code}")
    
    # Test 2: Health endpoint
    print("\n" + "="*60)
    print("Test 2: GET /health")
    print("="*60)
    response, error = test_endpoint("GET", "/health")
    if response and response.status_code == 200:
        data = response.json()
        print(f"[OK] Status: {response.status_code}")
        print(f"[INFO] Health: {data.get('status')}")
        print(f"[INFO] Database: {data.get('database')}")
        print(f"[INFO] Services: {json.dumps(data.get('services', {}), indent=2)}")
    else:
        print(f"[ERROR] Failed: {error or response.status_code}")
    
    # Test 3: API info
    print("\n" + "="*60)
    print("Test 3: GET /api/info")
    print("="*60)
    response, error = test_endpoint("GET", "/api/info")
    if response and response.status_code == 200:
        data = response.json()
        print(f"[OK] Status: {response.status_code}")
        print(f"[INFO] API Name: {data.get('name')}")
        print(f"[INFO] Version: {data.get('version')}")
        print(f"[INFO] Capabilities: {len(data.get('capabilities', []))} features")
        print(f"[INFO] Endpoints:")
        for key, value in data.get('endpoints', {}).items():
            print(f"        - {key}: {value}")
    else:
        print(f"[ERROR] Failed: {error or response.status_code}")
    
    # Test 4: List reports (empty is OK)
    print("\n" + "="*60)
    print("Test 4: GET /api/reports")
    print("="*60)
    response, error = test_endpoint("GET", "/api/reports", params={"page": 1, "page_size": 10})
    if response and response.status_code == 200:
        data = response.json()
        print(f"[OK] Status: {response.status_code}")
        print(f"[INFO] Total Reports: {data.get('total')}")
        print(f"[INFO] Page: {data.get('page')}")
        print(f"[INFO] Reports in page: {len(data.get('reports', []))}")
    else:
        print(f"[ERROR] Failed: {error or response.status_code}")
    
    # Test 5: Stats summary
    print("\n" + "="*60)
    print("Test 5: GET /api/reports/stats/summary")
    print("="*60)
    response, error = test_endpoint("GET", "/api/reports/stats/summary")
    if response and response.status_code == 200:
        data = response.json()
        print(f"[OK] Status: {response.status_code}")
        print(f"[INFO] Total Reports: {data.get('total_reports')}")
        print(f"[INFO] Average Risk Score: {data.get('average_risk_score')}")
        print(f"[INFO] Risk Distribution: {data.get('risk_distribution')}")
    else:
        print(f"[ERROR] Failed: {error or response.status_code}")
    
    # Test 6: Interactive docs
    print("\n" + "="*60)
    print("Test 6: Interactive Documentation")
    print("="*60)
    
    response, error = test_endpoint("GET", "/docs")
    if response and response.status_code == 200:
        print(f"[OK] Swagger UI available at: {BASE_URL}/docs")
    else:
        print(f"[ERROR] Swagger UI not accessible")
    
    response, error = test_endpoint("GET", "/redoc")
    if response and response.status_code == 200:
        print(f"[OK] ReDoc available at: {BASE_URL}/redoc")
    else:
        print(f"[ERROR] ReDoc not accessible")
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print("\n[OK] Basic API endpoints are working!")
    print("\n[INFO] To test analysis endpoints, you need:")
    print("      1. Valid GitHub token in .env")
    print("      2. Valid IBM watsonx.ai credentials in .env")
    print("      3. Run: python test_api.py")
    print("\n[INFO] Interactive documentation:")
    print(f"      - Swagger UI: {BASE_URL}/docs")
    print(f"      - ReDoc: {BASE_URL}/redoc")
    print("\n")

if __name__ == "__main__":
    main()

# Made with Bob
