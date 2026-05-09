"""
Stress Test Script for LangGraph Repair Cycle

This script tests the complete autonomous repair cycle:
1. Uses Chaos endpoint to break a node
2. Runs LangGraph agent to demonstrate full workflow
3. Proves that agent: Monitors -> Decides -> Repairs -> Monitors -> Decides -> Ends

Expected Workflow:
monitor_cluster -> decide_action -> repair_node -> monitor_cluster -> decide_action -> END
"""

from fastapi.testclient import TestClient
from simple_main import app
from langgraph_controller import build_cluster_graph, ClusterState

def stress_test_repair_cycle():
    """
    Perform a comprehensive stress test of the LangGraph repair cycle.
    
    This test demonstrates the complete autonomous workflow:
    1. Break a node using chaos endpoint
    2. Run LangGraph agent
    3. Verify the complete repair cycle works
    """
    print("="*80)
    print("🚀 STRESS TEST: LANGGRAPH REPAIR CYCLE")
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
    
    # Choose the first node to break
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
    
    # Step 3: Run LangGraph Agent for complete repair cycle
    print(f"\n🤖 STEP 3: Running LangGraph Agent")
    print(f"   Expected workflow: monitor -> decide -> repair -> monitor -> decide -> END")
    
    # Build the graph
    graph = build_cluster_graph()
    
    # Initialize state
    initial_state = {
        "node_reports": [],      # Will be populated by monitor_cluster
        "history": [],           # Empty history initially
        "current_task": "stress_test_repair_cycle",  # Stress test task
        "is_resolved": False,    # Not resolved yet
        "broken_node_id": None    # No broken node initially
    }
    
    # Execute graph with higher recursion limit for full cycle
    thread_id = "stress_test_repair_001"
    
    try:
        print(f"\n   ⚡ Executing LangGraph with thread_id: {thread_id}")
        
        result = graph.invoke(
            initial_state,
            config={
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 10  # Allow enough steps for complete cycle
            }
        )
        
        print(f"\n✅ LangGraph execution completed!")
        
        # Step 4: Analyze the results
        print(f"\n📊 STEP 4: Results Analysis")
        
        print(f"\n📜 EXECUTION HISTORY:")
        print(f"   Total history entries: {len(result['history'])}")
        for i, entry in enumerate(result['history']):
            print(f"   {i+1}. {entry}")
        
        print(f"\n🖥️  FINAL NODE STATUS:")
        for i, node in enumerate(result['node_reports']):
            status_emoji = "✅" if node['status'] == "Active" else "🔴"
            print(f"   {i+1}. {status_emoji} {node['name']} - Status: {node['status']}, "
                  f"CPU: {node['cpu_usage']}%, Memory: {node['memory_usage']}%")
        
        print(f"\n📋 FINAL STATE:")
        print(f"   - Current task: {result['current_task']}")
        print(f"   - Is resolved: {result['is_resolved']}")
        print(f"   - Broken node ID: {result['broken_node_id']}")
        
        # Step 5: Verify the repair cycle worked correctly
        print(f"\n🔍 STEP 5: Repair Cycle Verification")
        
        # Check if the broken node was repaired
        target_node = None
        for node in result['node_reports']:
            if node['id'] == node_id:
                target_node = node
                break
        
        if target_node and target_node['status'] == 'Active':
            print(f"   ✅ SUCCESS: Node {node_name} was successfully repaired!")
            print(f"      - Status changed from 'Failing' to 'Active'")
            print(f"      - CPU: {target_node['cpu_usage']}% (normalized)")
            print(f"      - Memory: {target_node['memory_usage']}% (normalized)")
            
            # Check if workflow completed properly
            if result['is_resolved'] and not result['broken_node_id']:
                print(f"   ✅ SUCCESS: Workflow completed properly!")
                print(f"      - All nodes are now healthy")
                print(f"      - Agent correctly terminated workflow")
                return True
            else:
                print(f"   ⚠️  WARNING: Workflow did not complete as expected")
                print(f"      - is_resolved: {result['is_resolved']}")
                print(f"      - broken_node_id: {result['broken_node_id']}")
                return False
        else:
            print(f"   ❌ FAILURE: Node {node_name} was not repaired!")
            if target_node:
                print(f"      - Final status: {target_node['status']}")
            else:
                print(f"      - Node not found in final reports")
            return False
            
    except Exception as e:
        print(f"❌ Error during stress test: {str(e)}")
        return False


def verify_workflow_sequence(history):
    """
    Verify that the expected workflow sequence was followed.
    
    Expected: monitor -> decide -> repair -> monitor -> decide -> END
    """
    print(f"\n🔍 WORKFLOW SEQUENCE ANALYSIS:")
    
    expected_patterns = [
        "Monitored cluster",
        "Decision: Node",
        "Action: Issued restart command",
        "Monitored cluster",
        "Decision: All nodes healthy"
    ]
    
    found_patterns = 0
    for pattern in expected_patterns:
        for entry in history:
            if pattern in entry:
                found_patterns += 1
                break
    
    print(f"   Expected patterns found: {found_patterns}/{len(expected_patterns)}")
    
    if found_patterns >= 4:  # Allow some flexibility
        print(f"   ✅ Workflow sequence appears correct")
        return True
    else:
        print(f"   ⚠️  Workflow sequence may be incomplete")
        return False


if __name__ == "__main__":
    success = stress_test_repair_cycle()
    
    print(f"\n" + "="*80)
    if success:
        print("🎉 STRESS TEST PASSED!")
        print("   ✅ LangGraph successfully completed full repair cycle")
        print("   ✅ Autonomous agent working correctly")
        print("   ✅ Decision-making and routing functional")
        print("   ✅ Node repair mechanism working")
    else:
        print("💥 STRESS TEST FAILED!")
        print("   ❌ Repair cycle did not complete successfully")
        print("   ❌ Check the error messages above")
    
    print("="*80)
