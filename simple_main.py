from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
from typing import Dict, List
import uuid

class NodeStatus(str, Enum):
    ACTIVE = "Active"
    FAILING = "Failing"
    OOM = "OOM"

class Node(BaseModel):
    id: str
    name: str
    status: NodeStatus
    cpu_usage: float
    memory_usage: float

# Global state management
nodes_db: Dict[str, Node] = {}

# Pre-populate with 5 active nodes
for i in range(5):
    node_id = str(uuid.uuid4())
    nodes_db[node_id] = Node(
        id=node_id,
        name=f"node-{i+1}",
        status=NodeStatus.ACTIVE,
        cpu_usage=10.0,
        memory_usage=10.0
    )

app = FastAPI(title="Mock Cluster Management API", description="A Kubernetes-like cluster simulation for testing autonomous AI agents")

@app.get("/nodes", response_model=List[Node])
async def list_nodes():
    """List all nodes and their current status."""
    return list(nodes_db.values())

@app.get("/nodes/{node_id}", response_model=Node)
async def get_node(node_id: str):
    """Get details for a specific node."""
    if node_id not in nodes_db:
        raise HTTPException(status_code=404, detail="Node not found")
    return nodes_db[node_id]

@app.post("/nodes/{node_id}/restart", response_model=Node)
async def restart_node(node_id: str):
    """Set the status of a node back to Active and reset CPU/Memory to 10%."""
    if node_id not in nodes_db:
        raise HTTPException(status_code=404, detail="Node not found")
    
    node = nodes_db[node_id]
    node.status = NodeStatus.ACTIVE
    node.cpu_usage = 10.0
    node.memory_usage = 10.0
    
    return node

@app.post("/nodes/{node_id}/fail", response_model=Node)
async def fail_node(node_id: str, fail_type: str = "Failing"):
    """Manually set a node's status to Failing or OOM to simulate a crash."""
    if node_id not in nodes_db:
        raise HTTPException(status_code=404, detail="Node not found")
    
    if fail_type not in ["Failing", "OOM"]:
        raise HTTPException(status_code=400, detail="fail_type must be 'Failing' or 'OOM'")
    
    node = nodes_db[node_id]
    if fail_type == "Failing":
        node.status = NodeStatus.FAILING
    else:
        node.status = NodeStatus.OOM
    node.cpu_usage = 95.0  # Simulate high resource usage
    node.memory_usage = 95.0
    
    return node

@app.post("/nodes/{node_id}/migrate", response_model=Node)
async def migrate_node(node_id: str):
    """Migrate workload away from a node by setting it to Inactive status."""
    if node_id not in nodes_db:
        raise HTTPException(status_code=404, detail="Node not found")
    
    node = nodes_db[node_id]
    node.status = "Inactive"  # Set to Inactive (simulating workload moved away)
    node.cpu_usage = 0.0  # Reset resources
    node.memory_usage = 0.0
    
    return node

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
