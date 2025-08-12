import os
import sys
import pytest

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_streamlit_files():
    """Test that all Streamlit dashboard files exist"""
    streamlit_files = [
        "Task1/simple_forecast_viz.py",
        "Task2/task2_streamlit.py",
        "Task3/streamlit.py",
        "Task5/streamlit.py",
        "Task6/steamlit.py"
    ]
    
    for file_path in streamlit_files:
        assert os.path.exists(file_path), f"Streamlit file {file_path} not found"

def test_main_task_files():
    """Test that main task files exist"""
    task_files = [
        "Task1/Forecasting.py",
        "Task2/best_of_infeed.py",
        "Task3/Trading.py",
        "Task5/invoice_generator.py",
        "Task6/task6_performance_report.py"
    ]
    
    for file_path in task_files:
        assert os.path.exists(file_path), f"Task file {file_path} not found"

def test_runner_files():
    """Test that task runner files exist"""
    runner_files = [
        "run_all_tasks.py",
        "run_all_streamlit.py",
        "requirements.txt",
        "README.md"
    ]
    
    for file_path in runner_files:
        assert os.path.exists(file_path), f"Runner file {file_path} not found"
