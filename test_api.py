"""
API Testing Script for PRISM
Tests all endpoints and validates responses.
"""
import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name: str):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Testing: {name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(message: str):
    print(f"{Colors.GREEN}[OK] {message}{Colors.END}")

def print_error(message: str):
    print(f"{Colors.RED}[ERROR] {message}{Colors.END}")

def print_info(message: str):
    print(f"{Colors.YELLOW}[INFO] {message}{Colors.END}")

def test_endpoint(method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
    """Test an API endpoint and return response."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, timeout=30)
        else:
            return None, f"Unsupported method: {method}"
        
        return response, None
    except requests.exceptions.ConnectionError:
        return None, "Connection failed - Is the server running?"
    except requests.exceptions.Timeout:
        return None, "Request timed out"
    except Exception as e:
        return None, str(e)

def test_health_endpoints():
    """Test health and info endpoints."""
    print_test("Health & Info Endpoints")
    
    # Test root endpoint
    print("\n1. Testing GET /")
    response, error = test_endpoint("GET", "/")
    if error:
        print_error(f"Failed: {error}")
        return False
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Status: {response.status_code}")
        print_info(f"Service: {data.get('service')}")
        print_info(f"Version: {data.get('version')}")
    else:
        print_error(f"Unexpected status: {response.status_code}")
        return False
    
    # Test health endpoint
    print("\n2. Testing GET /health")
    response, error = test_endpoint("GET", "/health")
    if error:
        print_error(f"Failed: {error}")
        return False
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Status: {response.status_code}")
        print_info(f"Health: {data.get('status')}")
        print_info(f"Database: {data.get('database')}")
    else:
        print_error(f"Unexpected status: {response.status_code}")
        return False
    
    # Test API info endpoint
    print("\n3. Testing GET /api/info")
    response, error = test_endpoint("GET", "/api/info")
    if error:
        print_error(f"Failed: {error}")
        return False
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Status: {response.status_code}")
        print_info(f"API Name: {data.get('name')}")
        print_info(f"Capabilities: {len(data.get('capabilities', []))} features")
    else:
        print_error(f"Unexpected status: {response.status_code}")
        return False
    
    return True

def test_analysis_endpoints():
    """Test analysis endpoints."""
    print_test("Analysis Endpoints")
    
    # Test analyze endpoint with a real PR
    print("\n1. Testing POST /api/analyze")
    print_info("Note: This requires valid GitHub credentials and may take time")
    
    analyze_data = {
        "pr_id": "1",
        "repository": "octocat/Hello-World"
    }
    
    print_info(f"Request: {json.dumps(analyze_data, indent=2)}")
    response, error = test_endpoint("POST", "/api/analyze", data=analyze_data)
    
    if error:
        print_error(f"Failed: {error}")
        return None
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Status: {response.status_code}")
        print_info(f"Report ID: {data.get('report_id')}")
        print_info(f"Risk Score: {data.get('risk_score')}")
        print_info(f"Risk Level: {data.get('risk_level')}")
        print_info(f"Changed Files: {len(data.get('changed_files', []))}")
        print_info(f"Impacted Nodes: {len(data.get('impacted_nodes', []))}")
        print_info(f"Analysis Duration: {data.get('analysis_duration')}s")
        return data.get('report_id')
    else:
        print_error(f"Status: {response.status_code}")
        print_error(f"Response: {response.text}")
        return None

def test_reports_endpoints(report_id: int = None):
    """Test reports endpoints."""
    print_test("Reports Endpoints")
    
    # Test list reports
    print("\n1. Testing GET /api/reports")
    response, error = test_endpoint("GET", "/api/reports", params={"page": 1, "page_size": 10})
    
    if error:
        print_error(f"Failed: {error}")
        return False
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Status: {response.status_code}")
        print_info(f"Total Reports: {data.get('total')}")
        print_info(f"Page: {data.get('page')}")
        print_info(f"Reports in page: {len(data.get('reports', []))}")
        
        # Get first report ID if we don't have one
        if not report_id and data.get('reports'):
            report_id = data['reports'][0]['id']
            print_info(f"Using report ID: {report_id} for further tests")
    else:
        print_error(f"Unexpected status: {response.status_code}")
    
    # Test get specific report
    if report_id:
        print(f"\n2. Testing GET /api/reports/{report_id}")
        response, error = test_endpoint("GET", f"/api/reports/{report_id}")
        
        if error:
            print_error(f"Failed: {error}")
        elif response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info(f"Report ID: {data.get('id')}")
            print_info(f"PR ID: {data.get('pr_id')}")
            print_info(f"Repository: {data.get('repository')}")
            print_info(f"Risk Level: {data.get('risk_level')}")
        else:
            print_error(f"Status: {response.status_code}")
    
    # Test get report by PR
    print("\n3. Testing GET /api/reports/pr/{pr_id}")
    response, error = test_endpoint(
        "GET", 
        "/api/reports/pr/1",
        params={"repository": "octocat/Hello-World"}
    )
    
    if error:
        print_error(f"Failed: {error}")
    elif response.status_code == 200:
        data = response.json()
        print_success(f"Status: {response.status_code}")
        print_info(f"Found report for PR 1")
    elif response.status_code == 404:
        print_info("No report found for this PR (expected if not analyzed yet)")
    else:
        print_error(f"Unexpected status: {response.status_code}")
    
    # Test stats summary
    print("\n4. Testing GET /api/reports/stats/summary")
    response, error = test_endpoint("GET", "/api/reports/stats/summary")
    
    if error:
        print_error(f"Failed: {error}")
    elif response.status_code == 200:
        data = response.json()
        print_success(f"Status: {response.status_code}")
        print_info(f"Total Reports: {data.get('total_reports')}")
        print_info(f"Average Risk Score: {data.get('average_risk_score')}")
        print_info(f"Risk Distribution: {data.get('risk_distribution')}")
    else:
        print_error(f"Unexpected status: {response.status_code}")
    
    return True

def test_batch_analysis():
    """Test batch analysis endpoint."""
    print_test("Batch Analysis Endpoint")
    
    print("\n1. Testing POST /api/analyze/batch")
    batch_data = [
        {"pr_id": "1", "repository": "octocat/Hello-World"},
        {"pr_id": "2", "repository": "octocat/Hello-World"}
    ]
    
    print_info(f"Queuing {len(batch_data)} analyses")
    response, error = test_endpoint("POST", "/api/analyze/batch", data=batch_data)
    
    if error:
        print_error(f"Failed: {error}")
        return False
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Status: {response.status_code}")
        print_info(f"Message: {data.get('message')}")
        print_info(f"Queued: {len(data.get('analyses', []))} analyses")
    else:
        print_error(f"Unexpected status: {response.status_code}")
        return False
    
    return True

def main():
    """Run all API tests."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}PRISM API Test Suite{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"\nBase URL: {BASE_URL}")
    print(f"Testing all endpoints...\n")
    
    # Check if server is running
    print_info("Checking if server is running...")
    response, error = test_endpoint("GET", "/")
    if error:
        print_error(f"Server is not running: {error}")
        print_info("Please start the server with: python -m backend.main")
        return
    
    print_success("Server is running!")
    
    # Run tests
    results = []
    
    # Test health endpoints
    results.append(("Health & Info", test_health_endpoints()))
    
    # Test analysis endpoints (may take time)
    print_info("\nAnalysis tests may take 10-30 seconds...")
    report_id = test_analysis_endpoints()
    results.append(("Analysis", report_id is not None))
    
    # Test reports endpoints
    results.append(("Reports", test_reports_endpoints(report_id)))
    
    # Test batch analysis
    results.append(("Batch Analysis", test_batch_analysis()))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Test Summary{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}PASSED{Colors.END}" if result else f"{Colors.RED}FAILED{Colors.END}"
        print(f"{name}: {status}")
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} test groups passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}🎉 All tests passed!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠ Some tests failed. Check the output above.{Colors.END}")

if __name__ == "__main__":
    main()

# Made with Bob
