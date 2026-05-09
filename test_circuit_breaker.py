"""
Circuit Breaker Test Script

This script tests the circuit breaker and escalation logic by creating a "stubborn" node
that appears to be repaired but stays broken, forcing the agent to escalate after 3 retries.

Expected Workflow:
1. Break node using chaos endpoint
2. Agent attempts repair (Retry #1) - node stays broken
3. Agent attempts repair (Retry #2) - node stays broken  
4. Agent attempts repair (Retry #3) - node stays broken
5. Agent escalates to human SRE
"""

from fastapi.testclient import TestClient
from simple_main import app
from langgraph_controller import build_cluster_graph, ClusterState

# Create a "stubborn" version of the Mock API that returns success but keeps node broken
class StubbornAPI:
    """Mock API that simulates a stubborn node that won't actually repair"""
    
    def __init__(self):
        self.client = TestClient(app)
        # Keep track of original nodes to simulate stubborn behavior
        self.original_nodes = {}
        self.broken_nodes = set()  # Track which nodes should stay broken
        
    def get_nodes(self):
        """Get nodes, but keep stubborn nodes broken"""
        response = self.client.get("/nodes")
        nodes = response.json()
        
        # Apply stubborn behavior - keep broken nodes broken
        for node in nodes:
            if node['id'] in self.broken_nodes:
                node['status'] = 'Failing'
                node['cpu_usage'] = 95.0
                node['memory_usage'] = 95.0
        
        return nodes
    
    def break_node(self, node_id, fail_type="Failing"):
        """Break a node and mark it as stubborn"""
        response = self.client.post(f"/nodes/{node_id}/fail?fail_type={fail_type}")
        broken_node = response.json()
        
        # Mark this node as stubborn - it will stay broken
        self.broken_nodes.add(node_id)
        
        print(f"   🔧 Marked node {broken_node['name']} as STUBBORN - it will stay broken")
        return broken_node
    
    def restart_node(self, node_id):
        """Attempt to restart stubborn node - returns success but node stays broken"""
        # Check if this node should stay stubborn (only first 3 attempts)
        current_attempt = getattr(self, '_restart_attempts', {})
        attempt_count = current_attempt.get(node_id, 0) + 1
        current_attempt[node_id] = attempt_count
        self._restart_attempts = current_attempt
        
        # Call the real restart endpoint
        response = self.client.post(f"/nodes/{node_id}/restart")
        restarted_node = response.json()
        
        # ALWAYS keep it stubborn for circuit breaker test - never allow it to be fixed
        restarted_node['status'] = 'Failing'
        restarted_node['cpu_usage'] = 95.0
        restarted_node['memory_usage'] = 95.0
        print(f"   🔄 Stubborn restart #{attempt_count}: API says success but node stays broken")
        
        return restarted_node


def test_circuit_breaker():
    """
    Test the circuit breaker and escalation logic with a stubborn node.
    """
    print("="*80)
    print("🚀 CIRCUIT BREAKER & ESCALATION TEST")
    print("="*80)
    
    # Create stubborn API wrapper
    stubborn_api = StubbornAPI()
    
    # Step 1: Get initial cluster state
    print("\n📋 STEP 1: Initial Cluster Assessment")
    nodes = stubborn_api.get_nodes()
    
    print(f"   Found {len(nodes)} nodes:")
    for i, node in enumerate(nodes):
        status_emoji = "✅" if node['status'] == "Active" else "🔴"
        print(f"   {i+1}. {status_emoji} {node['name']} - Status: {node['status']}, "
              f"CPU: {node['cpu_usage']}%, Memory: {node['memory_usage']}%")
    
    # Step 2: Break a node and make it stubborn
    print(f"\n💥 STEP 2: Breaking Node & Making it Stubborn")
    
    # Choose first node to break
    node_to_break = nodes[0]
    node_id = node_to_break['id']
    node_name = node_to_break['name']
    
    print(f"   Targeting: {node_name} ({node_id})")
    
    # Break the node and mark as stubborn
    broken_node = stubborn_api.break_node(node_id)
    
    print(f"   ✅ Node broken and marked as stubborn:")
    print(f"      - Name: {broken_node['name']}")
    print(f"      - Status: {broken_node['status']}")
    print(f"      - CPU: {broken_node['cpu_usage']}%")
    print(f"      - Memory: {broken_node['memory_usage']}%")
    
    # Step 3: Run LangGraph Agent with circuit breaker test
    print(f"\n🤖 STEP 3: Running LangGraph with Circuit Breaker")
    print(f"   Expected: 3 repair attempts → escalation to human SRE")
    
    # Build the graph
    graph = build_cluster_graph()
    
    # Initialize state with retry tracker
    initial_state = {
        "node_reports": [],      # Will be populated by monitor_cluster
        "history": [],           # Empty history initially
        "current_task": "circuit_breaker_test",  # Circuit breaker test task
        "is_resolved": False,    # Not resolved yet
        "broken_node_id": None,    # No broken node initially
        "retry_tracker": {}      # Empty retry tracker
    }
    
    # Execute graph with higher recursion limit for multiple cycles
    thread_id = "circuit_breaker_test_001"
    
    try:
        print(f"\n   ⚡ Executing LangGraph with circuit breaker test...")
        
        result = graph.invoke(
            initial_state,
            config={
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 15  # Allow enough steps for 3 repair attempts
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
            target_retry_count = result['retry_tracker'].get(node_id, 0)
            if target_retry_count == 3:
                print(f"      ✅ Retry count exactly 3 as expected")
                return True
            else:
                print(f"      ⚠️  Retry count is {target_retry_count}, expected 3")
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
    success = test_circuit_breaker()
    
    print(f"\n" + "="*80)
    if success:
        print("🎉 CIRCUIT BREAKER TEST PASSED!")
        print("   ✅ Circuit breaker logic working correctly")
        print("   ✅ Retry counter tracking functional")
        print("   ✅ Escalation triggered after 3 attempts")
        print("   ✅ Agent properly terminated for human intervention")
        print("   ✅ Workflow prevents infinite loops")
    else:
        print("💥 CIRCUIT BREAKER TEST FAILED!")
        print("   ❌ Circuit breaker logic not working")
        print("   ❌ Escalation did not trigger")
    
    print("="*80)
