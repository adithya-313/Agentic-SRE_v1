# Test the FastAPI app directly
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from simple_main import app

client = TestClient(app)

def test_direct():
    print("Testing FastAPI app directly...")
    
    # Test GET /nodes
    response = client.get("/nodes")
    print(f"GET /nodes - Status: {response.status_code}")
    if response.status_code == 200:
        nodes = response.json()
        print(f"Found {len(nodes)} nodes")
        print(f"First node: {nodes[0] if nodes else 'None'}")
    else:
        print(f"Error: {response.text}")
    
    # Test GET /docs
    response = client.get("/docs")
    print(f"GET /docs - Status: {response.status_code}")
    
    # Test root
    response = client.get("/")
    print(f"GET / - Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_direct()
