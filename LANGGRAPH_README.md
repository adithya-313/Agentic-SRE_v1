# LangGraph Cluster Management System

A complete system that combines a FastAPI Mock Cluster API with a LangGraph-based autonomous agent for cluster management.

## 🏗️ System Architecture

### Phase 1: Mock Cluster API
- **FastAPI Application**: Simulates a Kubernetes-like cluster
- **5 Pre-populated Nodes**: Each with status, CPU, and memory metrics
- **REST Endpoints**: Monitor, restart, and fail nodes
- **Auto-generated Documentation**: Available at `/docs`

### Phase 2: LangGraph Controller
- **State Management**: TypedDict-based state tracking
- **Monitoring Node**: Fetches cluster status from Mock API
- **Checkpointing**: MemorySaver for persistence
- **Thread-based Execution**: Isolated execution contexts

## 📁 File Structure

```
Agentic-SRE_v1/
├── simple_main.py              # Mock Cluster API (FastAPI)
├── langgraph_controller.py     # LangGraph-based autonomous agent
├── direct_test.py              # Direct API testing
├── test_api.py                 # HTTP API testing
├── requirements.txt            # Python dependencies
├── README.md                   # API documentation
└── LANGGRAPH_README.md         # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Mock Cluster API
```bash
python simple_main.py
```
The API will be available at `http://localhost:8000`

### 3. Run the LangGraph Controller
```bash
python langgraph_controller.py
```

## 📊 LangGraph State Structure

```python
class ClusterState(TypedDict):
    node_reports: List[dict]      # Latest status from Mock API
    history: Annotated[list, operator.add]  # Action log
    current_task: str             # Current agent focus
    is_resolved: bool            # Completion flag
```

## 🔧 Key Components

### Mock API Endpoints
- `GET /nodes` - List all nodes
- `GET /nodes/{id}` - Get specific node
- `POST /nodes/{id}/restart` - Reset node to Active
- `POST /nodes/{id}/fail` - Simulate node failure

### LangGraph Components
- **monitor_cluster()**: Fetches node data from Mock API
- **StateGraph**: Orchestrates the workflow
- **MemorySaver**: Provides persistence and checkpointing

## 🧪 Testing

### Direct API Test
```bash
python direct_test.py
```

### LangGraph Test
```bash
python langgraph_controller.py
```

## 📈 Sample Output

```
🚀 STARTING LANGGRAPH CLUSTER MANAGEMENT TEST
🔧 Building LangGraph for cluster management...
✅ LangGraph built successfully with MemorySaver checkpointer

⚡ Executing LangGraph with thread_id: cluster_test_001
✅ Cluster monitoring successful:
   - Found 5 nodes
   - Node 1: node-1 (Active)
   - Node 2: node-2 (Active)
   - Node 3: node-3 (Active)

📊 FINAL RESULTS:
   - History entries: 1
   - Node reports: 5

🖥️ NODE REPORTS:
   1. node-1 - Status: Active, CPU: 10.0%, Memory: 10.0%
   2. node-2 - Status: Active, CPU: 10.0%, Memory: 10.0%
   3. node-3 - Status: Active, CPU: 10.0%, Memory: 10.0%
   4. node-4 - Status: Active, CPU: 10.0%, Memory: 10.0%
   5. node-5 - Status: Active, CPU: 10.0%, Memory: 10.0%

🎉 Test completed successfully!
```

## 🔍 Key Features

✅ **Beginner-Friendly Code**: Clear comments and simple syntax
✅ **TypedDict State**: Strong typing for better code clarity
✅ **Error Handling**: Robust error management
✅ **Checkpointing**: MemorySaver for state persistence
✅ **Thread Isolation**: Separate execution contexts
✅ **Comprehensive Logging**: Detailed execution tracking

## 🎯 Next Steps

This foundation can be extended with:
- **Decision Nodes**: Logic to determine actions based on cluster state
- **Action Nodes**: Functions to restart/fail nodes automatically
- **Conditional Routing**: Dynamic workflow based on cluster conditions
- **Enhanced State**: More sophisticated state tracking
- **External Integrations**: Real cluster monitoring tools

## 🛠️ Dependencies

- `fastapi==0.104.1` - Mock API framework
- `uvicorn==0.24.0` - ASGI server
- `pydantic==2.5.0` - Data validation
- `langgraph` - Graph-based agent framework
- `langchain-core` - Core LangChain components
- `requests==2.31.0` - HTTP client library

## 📚 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **Pydantic**: https://pydantic-docs.helpmanual.io/
- **TypedDict**: https://docs.python.org/3/library/typing.html#typing.TypedDict
