import os
import subprocess
from datetime import datetime

def run_streamlit_apps():
    """Run all FlexPower Streamlit dashboards"""
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of Streamlit apps to run
    streamlit_apps = [
        {"path": "Task1/simple_forecast_viz.py", "port": 8500},
        {"path": "Task2/task2_streamlit.py", "port": 8501},
        {"path": "Task3/streamlit.py", "port": 8502},
        {"path": "Task5/streamlit_app.py", "port": 8503},  # Updated to new streamlit app
        {"path": "Task6/steamlit.py", "port": 8504}
    ]
    
    print("\n=== Starting FlexPower Streamlit Dashboards ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    processes = []
    for app in streamlit_apps:
        app_path = os.path.join(current_dir, app["path"])
        app_dir = os.path.dirname(app_path)
        
        if not os.path.exists(app_path):
            print(f"[ERROR] Dashboard not found: {app['path']}")
            continue
            
        print(f"\nStarting dashboard {app['path']}...")
        try:
            # Run the Streamlit app on specified port
            cmd = ['streamlit', 'run', app_path, '--server.port', str(app["port"])]
            process = subprocess.Popen(
                cmd,
                cwd=app_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            processes.append(process)
            print(f"✓ Started {app['path']} on http://localhost:{app['port']}")
        except Exception as e:
            print(f"✗ Error starting {app['path']}: {e}")
    
    print("\n=== All dashboards started ===")
    print("\nAvailable dashboards:")
    print("• Task 1 (Forecasting): http://localhost:8500")
    print("• Task 2 (Best of Infeed): http://localhost:8501")
    print("• Task 3 (Trading): http://localhost:8502")
    print("• Task 5 (Invoice Generator): http://localhost:8503")
    print("• Task 6 (Performance Report): http://localhost:8504")
    print("\nPress Ctrl+C to stop all dashboards\n")
    
    try:
        # Keep the script running until Ctrl+C
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        print("\nStopping all dashboards...")
        for process in processes:
            process.terminate()
        print("All dashboards stopped")

if __name__ == "__main__":
    run_streamlit_apps()
