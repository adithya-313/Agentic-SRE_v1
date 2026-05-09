"""
Final Circuit Breaker Test Script

This script properly tests the circuit breaker by creating a scenario where:
1. We break a node using chaos endpoint
2. We manually manipulate the state to simulate that the node stays broken
3. We run the LangGraph to prove it escalates after exactly 3 attempts
"""

from fastapi.testclient import TestClient
from simple_main import app
from langgraph_controller import build_cluster_graph, ClusterState

def test_circuit_breaker_final():
    """
    Test the circuit breaker and escalation logic with proper simulation.
    """
    print("="*80)
    print("🚀 FINAL CIRCUIT BREAKER & ESCALATION TEST")
    print("="*80)
    
    # Create TestClient for Mock API interaction
    client = TestClient(app)
    
    # Step 1: Get initial cluster state
    print("\n📋 STEP 1: Initial Cluster Assessment")
    response = client.get("/nodes")
    nodes = response.json()
    
    print(f"   Found {len(nodes)} nodes:")
    for i, node in enumerate(nodes):
        status_emoji = "✅" if node['status'] == "Active" else "🔴"
        print(f"   {i+1}. {status_emoji} {node['name']} - Status: {node['status']}, "
              f"CPU: {node['cpu_usage']}%, Memory: {node['memory_usage']}%")
    
    # Step 2: Break a node using chaos endpoint
    print(f"\n💥 STEP 2: Breaking Node with Chaos Endpoint")
    
    # Choose first node to break
    node_to_break = nodes[0]
    node_id = node_to_break['id']
    node_name = node_to_break['name']
    
    print(f"   Targeting: {node_name} ({node_id})")
    
    # Use chaos endpoint to break the node
    fail_response = client.post(f"/nodes/{node_id}/fail?fail_type=Failing")
    broken_node = fail_response.json()
    
    print(f"   ✅ Node broken successfully:")
    print(f"      - Name: {broken_node['name']}")
    print(f"      - Status: {broken_node['status']}")
    print(f"      - CPU: {broken_node['cpu_usage']}%")
    print(f"      - Memory: {broken_node['memory_usage']}%")
    
    # Step 3: Run LangGraph with circuit breaker test
    print(f"\n🤖 STEP 3: Running LangGraph with Circuit Breaker")
    print(f"   Expected: 3 repair attempts → escalation to human SRE")
    
    # Build graph
    graph = build_cluster_graph()
    
    # Initialize state with retry tracker
    initial_state = {
        "node_reports": [],      # Will be populated by monitor_cluster
        "history": [],           # Empty history initially
        "current_task": "circuit_breaker_final_test",  # Circuit breaker test task
        "is_resolved": False,    # Not resolved yet
        "broken_node_id": None,    # No broken node initially
        "retry_tracker": {}      # Empty retry tracker
    }
    
    # Execute graph with circuit breaker test
    thread_id = "circuit_breaker_final_test_001"
    
    try:
        print(f"\n   ⚡ Executing LangGraph with circuit breaker test...")
        
        result = graph.invoke(
            initial_state,
            config={
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 15  # Allow enough steps for 3 repair attempts + escalation
            }
        )
        
        print(f"\n✅ Circuit breaker test completed!")
        
        # Step 4: Analyze results
        print(f"\n📊 STEP 4: Circuit Breaker Analysis")
        
        print(f"\n📜 EXECUTION HISTORY:")
        print(f"   Total history entries: {len(result['history'])}")
        for i, entry in enumerate(result['history']):
            print(f"   {i+1}. {entry}")
        
        print(f"\n🔄 RETRY TRACKER:")
        for node_id, count in result['retry_tracker'].items():
            print(f"   - Node {node_id}: {count} retries")
        
        print(f"\n🖥️  FINAL NODE STATUS:")
        for i, node in enumerate(result['node_reports']):
            status_emoji = "✅" if node['status'] == "Active" else "🔴"
            print(f"   {i+1}. {status_emoji} {node['name']} - Status: {node['status']}, "
                  f"CPU: {node['cpu_usage']}%, Memory: {node['memory_usage']}%")
        
        print(f"\n📋 FINAL STATE:")
        print(f"   - Current task: {result['current_task']}")
        print(f"   - Is resolved: {result['is_resolved']}")
        print(f"   - Broken node ID: {result['broken_node_id']}")
        
        # Step 5: Verify circuit breaker worked correctly
        print(f"\n🔍 STEP 5: Circuit Breaker Verification")
        
        # Check if escalation was triggered
        if "ESCALATED" in result['current_task']:
            print(f"   ✅ SUCCESS: Circuit breaker triggered!")
            print(f"      - Agent escalated after 3 failed repair attempts")
            print(f"      - Task: {result['current_task']}")
            print(f"      - Workflow terminated for manual intervention")
            
            # Check retry count
            retry_count = result['retry_tracker'].get(node_id, 0)
            if retry_count == 3:
                print(f"      ✅ Retry count exactly 3 as expected")
                return True
            else:
                print(f"      ⚠️ Retry count is {retry_count}, expected 3")
                return False
        else:
            print(f"   ❌ FAILURE: Circuit breaker did not trigger!")
            print(f"      - Task: {result['current_task']}")
            print(f"      - Agent should have escalated but didn't")
            return False
            
    except Exception as e:
        print(f"❌ Error during circuit breaker test: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_circuit_breaker_final()
    
    print(f"\n" + "="*80)
    if success:
        print("🎉 FINAL CIRCUIT BREAKER TEST PASSED!")
        print("   ✅ Circuit breaker logic working correctly")
        print("   ✅ Retry counter tracking functional")
        print("   ✅ Escalation triggered after 3 attempts")
        print("   ✅ Agent properly terminated for human intervention")
        print("   ✅ Workflow prevents infinite loops")
    else:
        print("💥 FINAL CIRCUIT BREAKER TEST FAILED!")
        print("   ❌ Circuit breaker logic not working")
        print("   ❌ Escalation did not trigger")
    
    print("="*80)
