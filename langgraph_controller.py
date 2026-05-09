"""
LangGraph Controller for Mock Cluster Management

This file contains the foundational LangGraph structure that will control
our Mock Cluster API. It defines the state, monitoring function, and graph
construction with checkpointing capabilities.
"""

from typing import TypedDict, List, Annotated, Optional, Dict
import operator
import time
import requests
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver


# Define the state structure for our cluster management agent
class ClusterState(TypedDict):
    """
    Represents the current state of the cluster management system.
    
    Attributes:
        node_reports: List[dict] - Latest status reports from the Mock API
        history: Annotated[list, operator.add] - Running log of all actions taken
        current_task: str - The current focus of the agent
        is_resolved: bool - Flag to indicate if all issues are resolved
        broken_node_id: Optional[str] - ID of node that needs fixing (None if no broken nodes)
        retry_tracker: Dict[str, int] - Dictionary where Key is Node ID and Value is number of restart attempts
    """
    node_reports: List[dict]
    history: Annotated[list, operator.add]
    current_task: str
    is_resolved: bool
    broken_node_id: Optional[str]
    retry_tracker: Dict[str, int]


def monitor_cluster(state: ClusterState) -> ClusterState:
    """
    Monitor the cluster by fetching the latest node status from the Mock API.
    
    This function uses HTTP requests to call the running API at http://localhost:8000/nodes,
    updates the node_reports with the latest data, and logs the monitoring action.
    
    Args:
        state: Current cluster state containing history and other information
        
    Returns:
        Updated state with new node_reports and monitoring history entry
    """
    try:
        # Make GET request to the Mock API using HTTP requests
        response = requests.get("http://localhost:8000/nodes", timeout=5)
        
        if response.status_code == 200:
            # Successfully fetched node data
            nodes = response.json()
            
            # Update the state with new node reports
            state["node_reports"] = nodes
            
            # Add monitoring entry to history
            monitoring_message = f"Monitored cluster: found {len(nodes)} nodes"
            state["history"] = [monitoring_message]
            
            # Debug: Print node information
            print(f"✅ Cluster monitoring successful:")
            print(f"   - Found {len(nodes)} nodes")
            for i, node in enumerate(nodes[:3]):  # Show first 3 nodes
                print(f"   - Node {i+1}: {node['name']} ({node['status']})")
            
        else:
            # Handle API error
            error_message = f"Failed to monitor cluster: API returned status {response.status_code}"
            state["history"] = [error_message]
            print(f"❌ {error_message}")
            
    except Exception as e:
        # Handle any errors
        error_message = f"Failed to monitor cluster: {str(e)}"
        state["history"] = [error_message]
        print(f"❌ {error_message}")
    
    return state


def decide_action(state: ClusterState) -> ClusterState:
    """
    Decide what action to take based on cluster state and retry history.
    
    This function loops through node_reports to find first node
    that is not "Active" and selects dynamic strategy based on retry count.
    
    Args:
        state: Current cluster state with node reports and retry tracker
        
    Returns:
        Updated state with decision information and chosen strategy
    """
    print(f"🤔 Making decision based on cluster state...")
    
    # Reset broken_node_id to None initially
    state["broken_node_id"] = None
    
    # Loop through node reports to find broken nodes
    for node in state["node_reports"]:
        if node["status"] != "Active":
            # Found a broken node!
            broken_node_id = node["id"]
            broken_node_name = node["name"]
            
            # Check retry count for this node
            current_retry_count = state["retry_tracker"].get(broken_node_id, 0)
            print(f"   📊 Retry count for {broken_node_name}: {current_retry_count}")
            
            # Dynamic strategy selection based on retry count
            if current_retry_count == 0:
                # First attempt: Try RESTART
                strategy = "RESTART_REQUIRED"
                state["current_task"] = f"RESTART_REQUIRED for {broken_node_id}"
                state["broken_node_id"] = broken_node_id
                state["is_resolved"] = False
                
                # Add decision to history
                decision_message = f"Strategy: First failure detected. Attempting RESTART for {broken_node_name} ({broken_node_id})."
                state["history"] = [decision_message]
                
                print(f"🔴 Found broken node:")
                print(f"   - Node: {broken_node_name}")
                print(f"   - ID: {broken_node_id}")
                print(f"   - Status: {node['status']}")
                print(f"   - Retry count: {current_retry_count} (first attempt)")
                print(f"   - Strategy: {strategy}")
                print(f"   - Task: {state['current_task']}")
                
            elif current_retry_count == 1:
                # Second attempt: Try MIGRATION
                strategy = "MIGRATE_REQUIRED"
                state["current_task"] = f"MIGRATE_REQUIRED for {broken_node_id}"
                state["broken_node_id"] = broken_node_id
                state["is_resolved"] = False
                
                # Add decision to history
                decision_message = f"Strategy: Restart failed, attempting MIGRATION for {broken_node_name} ({broken_node_id})."
                state["history"] = [decision_message]
                
                print(f"🔴 Found broken node:")
                print(f"   - Node: {broken_node_name}")
                print(f"   - ID: {broken_node_id}")
                print(f"   - Status: {node['status']}")
                print(f"   - Retry count: {current_retry_count} (restart failed)")
                print(f"   - Strategy: {strategy}")
                print(f"   - Task: {state['current_task']}")
                
            elif current_retry_count >= 2:
                # Third+ attempt: ESCALATE
                strategy = "ESCALATED"
                state["current_task"] = "ESCALATED: Strategy Exhausted"
                state["is_resolved"] = True  # Stop the loop
                
                # Add escalation message to history
                escalation_message = f"CRITICAL: Node {broken_node_name} ({broken_node_id}) failed after {current_retry_count} attempts. All strategies exhausted. Escalating to human SRE."
                state["history"] = [escalation_message]
                
                print(f"🚨 ESCALATION TRIGGERED:")
                print(f"   - Node: {broken_node_name}")
                print(f"   - ID: {broken_node_id}")
                print(f"   - Status: {node['status']}")
                print(f"   - Retry count: {current_retry_count} (≥ 2, escalating)")
                print(f"   - Strategy: {strategy}")
                print(f"   - Task: {state['current_task']}")
                print(f"   - Action: Workflow terminated for manual intervention")
            
            return state
    
    # No broken nodes found - all is healthy!
    state["current_task"] = "All nodes are healthy"
    state["is_resolved"] = True
    
    # Add completion message to history
    completion_message = "Decision: All nodes healthy. Task complete."
    state["history"] = [completion_message]
    
    print(f"✅ All nodes are healthy!")
    print(f"   - Task: {state['current_task']}")
    print(f"   - Resolved: {state['is_resolved']}")
    
    return state


def should_continue(state: ClusterState) -> str:
    """
    Router function that determines the next step in the workflow.
    
    This function checks if the task is resolved and routes accordingly:
    - If resolved: return "end" to finish the workflow
    - If not resolved: return "repair" to continue fixing nodes
    
    Args:
        state: Current cluster state
        
    Returns:
        String indicating the next step: "end" or "repair"
    """
    print(f"🚦 Routing decision:")
    
    if state["is_resolved"]:
        print(f"   → Task is resolved. Ending workflow.")
        return "end"
    else:
        if state["broken_node_id"]:
            print(f"   → Found broken node {state['broken_node_id']}. Continuing to repair.")
        else:
            print(f"   → Task not resolved. Continuing workflow.")
        return "repair"


def repair_node(state: ClusterState) -> ClusterState:
    """
    Traffic Controller: Execute different strategies based on current_task.
    
    This function acts as a dispatcher that calls different API endpoints
    based on the strategy chosen by decide_action:
    - RESTART_REQUIRED: Calls /restart endpoint
    - MIGRATE_REQUIRED: Calls /migrate endpoint
    - Always increments retry tracker and clears broken_node_id
    
    Args:
        state: Current cluster state with broken_node_id and retry_tracker
        
    Returns:
        Updated state with action logged and broken_node_id cleared
    """
    print(f"🔧 Traffic Controller: Executing strategy...")
    
    # Check if we have a broken node to repair
    if not state["broken_node_id"]:
        # No broken node to repair
        state["history"] = ["Action: No broken node found to repair."]
        print(f"   ℹ️ No broken node found to repair.")
        return state
    
    broken_node_id = state["broken_node_id"]
    current_task = state["current_task"]
    
    try:
        # Execute strategy based on current_task
        if "RESTART_REQUIRED" in current_task:
            # Strategy 1: Restart the node
            print(f"   🔄 Executing RESTART strategy for {broken_node_id}")
            print(f"   ⏳ Simulating real server restart (2 seconds)...")
            time.sleep(2)  # Simulate real server restart time
            response = requests.post(f"http://localhost:8000/nodes/{broken_node_id}/restart", timeout=5)
            
            if response.status_code == 200:
                repaired_node = response.json()
                action_message = f"Action: RESTART executed for Node {broken_node_id}. Status: {repaired_node['status']}"
            else:
                action_message = f"Action: RESTART failed for Node {broken_node_id}. Status: {response.status_code}"
                
        elif "MIGRATE_REQUIRED" in current_task:
            # Strategy 2: Migrate workload away from node
            print(f"   🚚 Executing MIGRATE strategy for {broken_node_id}")
            response = requests.post(f"http://localhost:8000/nodes/{broken_node_id}/migrate", timeout=5)
            
            if response.status_code == 200:
                migrated_node = response.json()
                action_message = f"Action: MIGRATION executed for Node {broken_node_id}. Status: {migrated_node['status']}"
            else:
                action_message = f"Action: MIGRATION failed for Node {broken_node_id}. Status: {response.status_code}"
                
        else:
            # Unknown strategy
            action_message = f"Action: Unknown strategy '{current_task}' for Node {broken_node_id}"
            print(f"   ❌ Unknown strategy: {current_task}")
        
        # Increment retry counter for this node (regardless of strategy)
        current_retry_count = state["retry_tracker"].get(broken_node_id, 0)
        new_retry_count = current_retry_count + 1
        state["retry_tracker"][broken_node_id] = new_retry_count
        
        # Add action to history
        state["history"] = [action_message]
        
        # CRUCIAL: Clear broken_node_id to prevent infinite loops
        state["broken_node_id"] = None
        state["current_task"] = "Strategy executed - monitoring again"
        
        print(f"   ✅ Strategy execution completed:")
        print(f"      - Strategy: {current_task}")
        print(f"      - Node ID: {broken_node_id}")
        print(f"      - Attempt #{new_retry_count}")
        print(f"      - broken_node_id cleared: {state['broken_node_id']}")
        
        # Simulate server reboot time (2 seconds)
        print(f"   ⏳ Simulating server reboot (2 seconds)...")
        time.sleep(2)
            
    except Exception as e:
        # Handle any errors
        error_message = f"Action: Error executing strategy for Node {broken_node_id}: {str(e)}"
        state["history"] = [error_message]
        print(f"   ❌ {error_message}")
        
        # Even on error, simulate reboot time
        print(f"   ⏳ Simulating server reboot (2 seconds)...")
        time.sleep(2)
    
    return state


def build_cluster_graph() -> StateGraph:
    """
    Build and configure the LangGraph for cluster management.
    
    This function creates a StateGraph, adds monitor and decision nodes,
    sets up conditional routing, and compiles it with a MemorySaver checkpointer.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    print("🔧 Building LangGraph for cluster management...")
    
    # Initialize the StateGraph with our ClusterState
    workflow = StateGraph(ClusterState)
    
    # Add nodes to the workflow
    workflow.add_node("monitor_cluster", monitor_cluster)
    workflow.add_node("decide_action", decide_action)
    workflow.add_node("repair_node", repair_node)
    
    # Set the entry point - where the graph starts
    workflow.set_entry_point("monitor_cluster")
    
    # Add edges between nodes
    # From monitor_cluster to decide_action (monitoring leads to decision)
    workflow.add_edge("monitor_cluster", "decide_action")
    
    # Add conditional edge from decide_action
    # This will route to "repair" (to repair_node) or "end" based on should_continue function
    workflow.add_conditional_edges(
        "decide_action",           # Source node
        should_continue,            # Router function
        {
            "repair": "repair_node",   # If not resolved, go to repair_node
            "end": END                 # If resolved, end the workflow
        }
    )
    
    # Add normal edge from repair_node back to monitor_cluster
    # This creates the complete cycle: monitor -> decide -> repair -> monitor
    workflow.add_edge("repair_node", "monitor_cluster")
    
    # Create a MemorySaver checkpointer for persistence
    checkpointer = MemorySaver()
    
    # Compile the graph with the checkpointer
    compiled_graph = workflow.compile(checkpointer=checkpointer)
    
    print("✅ LangGraph built successfully with:")
    print("   - monitor_cluster node")
    print("   - decide_action node")
    print("   - repair_node node")
    print("   - Conditional routing with should_continue")
    print("   - MemorySaver checkpointer")
    return compiled_graph


def run_cluster_test():
    """
    Test the LangGraph by running it with a thread_id and printing results.
    
    This function demonstrates how to execute the compiled graph and
    verify that the monitoring functionality works correctly.
    """
    print("\n" + "="*60)
    print("🚀 STARTING LANGGRAPH CLUSTER MANAGEMENT TEST")
    print("="*60)
    
    # Build the graph
    graph = build_cluster_graph()
    
    # Initialize the starting state
    initial_state = {
        "node_reports": [],      # Empty list initially
        "history": [],           # Empty history initially
        "current_task": "initial_monitoring",  # Starting task
        "is_resolved": False,    # Not resolved yet
        "broken_node_id": None    # No broken node initially
    }
    
    # Define a unique thread_id for this execution
    thread_id = "cluster_test_001"
    
    print(f"\n📋 Initial state prepared:")
    print(f"   - Thread ID: {thread_id}")
    print(f"   - Current task: {initial_state['current_task']}")
    print(f"   - Node reports: {len(initial_state['node_reports'])}")
    print(f"   - History entries: {len(initial_state['history'])}")
    print(f"   - Broken node ID: {initial_state['broken_node_id']}")
    
    try:
        # Run the graph with the specified thread_id
        print(f"\n⚡ Executing LangGraph with thread_id: {thread_id}")
        
        # Execute the graph and get the final state
        result = graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": thread_id}}
        )
        
        print("\n✅ Graph execution completed successfully!")
        
        # Print the results to verify it worked
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
            print(f"   {i+1}. {node['name']} - Status: {node['status']}, "
                  f"CPU: {node['cpu_usage']}%, Memory: {node['memory_usage']}%")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during graph execution: {str(e)}")
        return None


# This block runs when the script is executed directly
if __name__ == "__main__":
    # Run the test
    final_state = run_cluster_test()
    
    if final_state:
        print(f"\n🎉 Test completed successfully!")
        print(f"   The LangGraph successfully monitored the mock cluster.")
    else:
        print(f"\n💥 Test failed. Check the error messages above.")
