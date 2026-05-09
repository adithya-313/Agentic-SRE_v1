import requests
import json

# Test the API endpoints
base_url = "http://localhost:8000"

def test_api():
    try:
        # Test GET /nodes
        print("Testing GET /nodes...")
        response = requests.get(f"{base_url}/nodes")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            nodes = response.json()
            print(f"Found {len(nodes)} nodes")
            if nodes:
                node_id = nodes[0]['id']
                print(f"First node ID: {node_id}")
                
                # Test GET /nodes/{id}
                print(f"\nTesting GET /nodes/{node_id}...")
                response = requests.get(f"{base_url}/nodes/{node_id}")
                print(f"Status: {response.status_code}")
                print(f"Node details: {response.json()}")
                
                # Test POST /nodes/{id}/restart
                print(f"\nTesting POST /nodes/{node_id}/restart...")
                response = requests.post(f"{base_url}/nodes/{node_id}/restart")
                print(f"Status: {response.status_code}")
                print(f"Restarted node: {response.json()}")
                
                # Test POST /nodes/{id}/fail
                print(f"\nTesting POST /nodes/{node_id}/fail...")
                response = requests.post(f"{base_url}/nodes/{node_id}/fail?fail_type=Failing")
                print(f"Status: {response.status_code}")
                print(f"Failed node: {response.json()}")
            else:
                print("No nodes found")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    test_api()
