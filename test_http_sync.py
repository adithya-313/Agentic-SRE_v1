"""
Test script to verify HTTP sync is working correctly.
This should fail if the API is not running.
"""

import requests
from langgraph_controller import build_cluster_graph, ClusterState

def test_http_sync():
    """Test that HTTP sync works and requires API to be running."""
    print("🧪 Testing HTTP Sync...")
    
    try:
        # Test 1: Direct HTTP request to API
        print("1. Testing direct HTTP request...")
        response = requests.get("http://localhost:8000/nodes", timeout=2)
        if response.status_code == 200:
            nodes = response.json()
            print(f"   ✅ API accessible: Found {len(nodes)} nodes")
        else:
            print(f"   ❌ API returned status {response.status_code}")
            return False
            
        # Test 2: LangGraph controller using HTTP
        print("2. Testing LangGraph controller with HTTP...")
        graph = build_cluster_graph()
        
        initial_state = {
            "node_reports": [],
            "history": [],
            "current_task": "Initial check",
            "is_resolved": False,
            "broken_node_id": None,
            "retry_tracker": {}
        }
        
        result = graph.invoke(
            initial_state,
            config={
                "configurable": {"thread_id": "test_http_sync"},
                "recursion_limit": 5
            }
        )
        
        if result and "node_reports" in result:
            print(f"   ✅ LangGraph HTTP sync successful")
            print(f"   📊 Monitored {len(result['node_reports'])} nodes")
            return True
        else:
            print(f"   ❌ LangGraph HTTP sync failed")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API at http://localhost:8000")
        print("   💡 Make sure the API is running: python simple_main.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_http_sync()
    if success:
        print("\n✅ HTTP Sync Test PASSED")
        print("🚀 All components are using HTTP communication")
    else:
        print("\n❌ HTTP Sync Test FAILED")
        print("🔧 Requires API to be running on port 8000")
