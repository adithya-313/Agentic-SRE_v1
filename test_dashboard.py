"""
Test script to demonstrate the dashboard functionality.
This runs a quick test of the dashboard with the Mock API.
"""

import time
import threading
from simple_main import app
from fastapi.testclient import TestClient
from dashboard import SREDashboard

def test_dashboard():
    """Test dashboard functionality with Mock API."""
    print("🧪 Testing SRE Dashboard...")
    
    # Create TestClient (simulates running API)
    client = TestClient(app)
    
    # Test API connection
    response = client.get('/nodes')
    nodes = response.json()
    print(f"✅ API connected: Found {len(nodes)} nodes")
    
    # Create dashboard instance
    dashboard = SREDashboard("http://localhost:8000")
    
    # Test dashboard rendering (single frame)
    print("\n📊 Testing dashboard rendering...")
    dashboard.create_rich_dashboard(nodes) if hasattr(dashboard, 'console') else dashboard.create_simple_dashboard(nodes)
    
    print("\n✅ Dashboard test completed!")
    print("🚀 To run the live dashboard:")
    print("   1. Start API: python simple_main.py")
    print("   2. Run dashboard: python dashboard.py")
    print("   3. Press Ctrl+C to stop")

if __name__ == "__main__":
    test_dashboard()
