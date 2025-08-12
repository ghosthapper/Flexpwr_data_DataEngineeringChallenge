import os
import subprocess
from datetime import datetime

def run_tasks():
    """Run all FlexPower tasks in sequence"""
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of tasks to run in order
    tasks = [
        "Task1/Forecasting.py",
        "Task2/best_of_infeed.py",
        "Task3/Trading.py",
        "Task5/simple_invoice_generator.py",  # Using the simplified version
        "Task6/task6_performance_report.py"
    ]
    
    print("\n=== Starting FlexPower Tasks ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    for task in tasks:
        task_path = os.path.join(current_dir, task)
        task_dir = os.path.dirname(task_path)
        
        if not os.path.exists(task_path):
            print(f"[ERROR] Task not found: {task}")
            continue
            
        print(f"\nRunning {task}...")
        try:
            # Run the task in its directory
            process = subprocess.run(
                ['python', task_path],
                cwd=task_dir,
                check=True
            )
            print(f"✓ Completed {task}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error running {task}: {e}")
            
    print("\n=== All tasks processed ===")

if __name__ == "__main__":
    run_tasks()
