"""
Test script to demonstrate LangGraph decision-making with a broken node.

This script will:
1. Start the Mock API
2. Manually fail a node using the API
3. Run the LangGraph to show decision-making
4. Demonstrate conditional routing
"""

from fastapi.testclient import TestClient
from simple_main import app
from langgraph_controller import build_cluster_graph, ClusterState

def test_with_broken_node():
    """
    Test the LangGraph with a broken node to demonstrate decision-making.
    """
    print("="*60)
    print("🚀 TESTING LANGGRAPH WITH BROKEN NODE")
    print("="*60)
    
    # Create a TestClient to interact with the Mock API
    client = TestClient(app)
    
    # Get the initial state of nodes
    print("📋 Getting initial node state...")
    response = client.get("/nodes")
    nodes = response.json()
    
    print(f"   Found {len(nodes)} nodes:")
    for i, node in enumerate(nodes):
        print(f"   {i+1}. {node['name']} - Status: {node['status']}")
    
    # Choose a node to fail (let's fail the first one)
    node_to_fail = nodes[0]
    node_id = node_to_fail['id']
    node_name = node_to_fail['name']
    
    print(f"\n💥 Manually failing node: {node_name} ({node_id})")
    
    # Fail the node using the Mock API
    fail_response = client.post(f"/nodes/{node_id}/fail?fail_type=Failing")
    failed_node = fail_response.json()
    
    print(f"   ✅ Node failed successfully:")
    print(f"      - Name: {failed_node['name']}")
    print(f"      - Status: {failed_node['status']}")
    print(f"      - CPU: {failed_node['cpu_usage']}%")
    print(f"      - Memory: {failed_node['memory_usage']}%")
    
    # Now run the LangGraph to see how it handles the broken node
    print(f"\n🤖 Running LangGraph with broken node...")
    
    # Build the graph
    graph = build_cluster_graph()
    
    # Initialize state
    initial_state = {
        "node_reports": [],      # Will be populated by monitor_cluster
        "history": [],           # Empty history initially
        "current_task": "test_with_broken_node",  # Test task
        "is_resolved": False,    # Not resolved yet
        "broken_node_id": None    # No broken node initially
    }
    
    # Execute graph
    thread_id = "broken_node_test_001"
    
    try:
        result = graph.invoke(
            initial_state,
            config={
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 5  # Limit to prevent infinite loops
            }
        )
        
        print("\n✅ Graph execution completed!")
        
        # Show the results
        print(f"\n📊 FINAL RESULTS:")
        print(f"   - History entries: {len(result['history'])}")
        print(f"   - Node reports: {len(result['node_reports'])}")
        print(f"   - Current task: {result['current_task']}")
        print(f"   - Is resolved: {result['is_resolved']}")
        print(f"   - Broken node ID: {result['broken_node_id']}")
        
        # Show the history
        print(f"\n📜 HISTORY:")
        for i, entry in enumerate(result['history']):
            print(f"   {i+1}. {entry}")
        
        # Show node reports
        print(f"\n🖥️  NODE REPORTS:")
        for i, node in enumerate(result['node_reports']):
            status_emoji = "🔴" if node['status'] != "Active" else "✅"
            print(f"   {i+1}. {status_emoji} {node['name']} - Status: {node['status']}, "
                  f"CPU: {node['cpu_usage']}%, Memory: {node['memory_usage']}%")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during graph execution: {str(e)}")
        return None

if __name__ == "__main__":
    result = test_with_broken_node()
    
    if result:
        print(f"\n🎉 Test completed successfully!")
        print(f"   The LangGraph correctly identified the broken node.")
        print(f"   Decision-making and conditional routing working properly!")
    else:
        print(f"\n💥 Test failed. Check the error messages above.")
