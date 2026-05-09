"""
Real-time SRE Dashboard

This script provides a live monitoring dashboard for the Mock API nodes,
displaying current status, resource usage, and health metrics in a
pretty table format that updates every second.
"""

import time
import os
import sys
from datetime import datetime
from typing import List, Dict
import requests

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: rich library not found. Using simple table format.")
    print("Install with: pip install rich")

class SREDashboard:
    """Real-time SRE monitoring dashboard."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.console = Console() if RICH_AVAILABLE else None
        self.start_time = datetime.now()
        
    def get_nodes(self) -> List[Dict]:
        """Fetch current node status from Mock API."""
        try:
            response = requests.get(f"{self.api_url}/nodes", timeout=2)
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except requests.exceptions.RequestException:
            return []
    
    def get_status_color(self, status: str) -> str:
        """Get color code for node status."""
        status_colors = {
            "Active": "green",
            "Failing": "red", 
            "OOM": "yellow",
            "Inactive": "blue"
        }
        return status_colors.get(status, "white")
    
    def get_status_emoji(self, status: str) -> str:
        """Get emoji for node status."""
        status_emojis = {
            "Active": "✅",
            "Failing": "🔴",
            "OOM": "⚠️",
            "Inactive": "💤"
        }
        return status_emojis.get(status, "❓")
    
    def create_rich_dashboard(self, nodes: List[Dict]) -> None:
        """Create rich dashboard layout."""
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Create header
        header = Panel(
            Align.center(Text("🚀 AGENTIC SRE DASHBOARD", style="bold blue")),
            border_style="blue",
            padding=(1, 2)
        )
        
        # Create main table
        table = Table(title="Node Status Monitor", show_header=True, header_style="bold magenta")
        table.add_column("Node", style="cyan", width=12)
        table.add_column("Status", style="bold", width=10)
        table.add_column("CPU %", style="yellow", width=8)
        table.add_column("Memory %", style="yellow", width=10)
        table.add_column("Node ID", style="dim", width=20)
        
        # Add nodes to table
        for node in nodes:
            status = node.get('status', 'Unknown')
            cpu = node.get('cpu_usage', 0)
            memory = node.get('memory_usage', 0)
            name = node.get('name', 'Unknown')
            node_id = node.get('id', 'Unknown')
            
            # Color code based on status
            status_style = self.get_status_color(status)
            status_text = f"{self.get_status_emoji(status)} {status}"
            
            # Color code resource usage
            cpu_style = "red" if cpu > 80 else "yellow" if cpu > 50 else "green"
            memory_style = "red" if memory > 80 else "yellow" if memory > 50 else "green"
            
            table.add_row(
                name,
                Text(status_text, style=status_style),
                Text(f"{cpu:.1f}%", style=cpu_style),
                Text(f"{memory:.1f}%", style=memory_style),
                Text(node_id[:20] + "..." if len(node_id) > 20 else node_id, style="dim")
            )
        
        # Create summary panel
        total_nodes = len(nodes)
        active_nodes = sum(1 for n in nodes if n.get('status') == 'Active')
        failing_nodes = sum(1 for n in nodes if n.get('status') == 'Failing')
        oom_nodes = sum(1 for n in nodes if n.get('status') == 'OOM')
        inactive_nodes = sum(1 for n in nodes if n.get('status') == 'Inactive')
        
        summary_text = f"""
Total Nodes: {total_nodes} | 
Active: {active_nodes} | 
Failing: {failing_nodes} | 
OOM: {oom_nodes} | 
Inactive: {inactive_nodes}
        """.strip()
        
        summary = Panel(
            Text(summary_text, style="bold white"),
            title="Cluster Summary",
            border_style="green",
            padding=(1, 2)
        )
        
        # Create timestamp panel
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uptime = datetime.now() - self.start_time
        uptime_str = str(uptime).split('.')[0]
        
        timestamp_text = f"""
Last Update: {current_time}
Dashboard Uptime: {uptime_str}
API Endpoint: {self.api_url}
        """.strip()
        
        timestamp = Panel(
            Text(timestamp_text, style="dim"),
            title="System Info",
            border_style="cyan",
            padding=(1, 2)
        )
        
        # Layout and render
        layout = Layout()
        layout.split_column(
            Layout(header, size=3),
            Layout(table, size=20),
            Layout(summary, size=3),
            Layout(timestamp, size=5)
        )
        
        self.console.print(layout)
    
    def create_simple_dashboard(self, nodes: List[Dict]) -> None:
        """Create simple text dashboard (fallback)."""
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Header
        print("=" * 80)
        print("🚀 AGENTIC SRE DASHBOARD".center(80))
        print("=" * 80)
        
        # Summary
        total_nodes = len(nodes)
        active_nodes = sum(1 for n in nodes if n.get('status') == 'Active')
        failing_nodes = sum(1 for n in nodes if n.get('status') == 'Failing')
        oom_nodes = sum(1 for n in nodes if n.get('status') == 'OOM')
        inactive_nodes = sum(1 for n in nodes if n.get('status') == 'Inactive')
        
        print(f"Cluster Summary: Total: {total_nodes} | Active: {active_nodes} | "
              f"Failing: {failing_nodes} | OOM: {oom_nodes} | Inactive: {inactive_nodes}")
        print("-" * 80)
        
        # Table header
        print(f"{'Node':<12} {'Status':<12} {'CPU %':<8} {'Memory %':<10} {'Node ID':<20}")
        print("-" * 80)
        
        # Node data
        for node in nodes:
            status = node.get('status', 'Unknown')
            cpu = node.get('cpu_usage', 0)
            memory = node.get('memory_usage', 0)
            name = node.get('name', 'Unknown')
            node_id = node.get('id', 'Unknown')
            
            status_emoji = self.get_status_emoji(status)
            
            print(f"{name:<12} {status_emoji} {status:<10} {cpu:<8.1f} {memory:<10.1f} "
                  f"{node_id[:20] + '...' if len(node_id) > 20 else node_id:<20}")
        
        # Footer
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uptime = datetime.now() - self.start_time
        uptime_str = str(uptime).split('.')[0]
        
        print("-" * 80)
        print(f"Last Update: {current_time} | Uptime: {uptime_str} | API: {self.api_url}")
        print("=" * 80)
    
    def run(self) -> None:
        """Run the dashboard in a continuous loop."""
        print("🚀 Starting SRE Dashboard...")
        print(f"📡 Connecting to API at: {self.api_url}")
        print("⏹️  Press Ctrl+C to stop")
        print()
        
        # Test API connection
        try:
            test_nodes = self.get_nodes()
            if not test_nodes:
                print(f"❌ Could not connect to API at {self.api_url}")
                print("Make sure the Mock API is running: python simple_main.py")
                return
            print(f"✅ Connected to API! Found {len(test_nodes)} nodes")
            print()
            time.sleep(2)
        except Exception as e:
            print(f"❌ API connection error: {e}")
            return
        
        # Main dashboard loop
        try:
            while True:
                nodes = self.get_nodes()
                
                if RICH_AVAILABLE:
                    self.create_rich_dashboard(nodes)
                else:
                    self.create_simple_dashboard(nodes)
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard stopped by user")
        except Exception as e:
            print(f"\n❌ Dashboard error: {e}")


def main():
    """Main entry point."""
    # Check if API is running on different port
    api_url = "http://localhost:8000"
    
    # Allow command line argument for custom API URL
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    
    dashboard = SREDashboard(api_url)
    dashboard.run()


if __name__ == "__main__":
    main()
