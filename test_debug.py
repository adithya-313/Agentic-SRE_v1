import requests
import json

# Test the debug API endpoints
base_url = "http://localhost:8000"

def test_debug_api():
    try:
        # Test GET /
        print("Testing GET /...")
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test GET /test
        print(f"\nTesting GET /test...")
        response = requests.get(f"{base_url}/test")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
            
    except Exception as e:
        print(f"Error testing debug API: {e}")

if __name__ == "__main__":
    test_debug_api()
