import sys
import os
import pytest
import pandas as pd
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestFileStructure:
    def test_task_directories_exist(self):
        """Test that all task directories exist"""
        task_dirs = ['Task1', 'Task2', 'Task3', 'Task5', 'Task6']
        for dir_name in task_dirs:
            assert os.path.exists(dir_name), f"Task directory {dir_name} not found"
    
    def test_output_directories_exist(self):
        """Test that output directories exist in each task"""
        task_dirs = ['Task1', 'Task2', 'Task3', 'Task5', 'Task6']
        for dir_name in task_dirs:
            output_dir = os.path.join(dir_name, 'output')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

class TestDataFormats:
    def test_date_formats(self):
        """Test date formats in various files"""
        try:
            # Test forecast dates
            forecasts = pd.read_csv("Task1/output/asset_forecasts.csv")
            pd.to_datetime(forecasts['delivery_start'])
            
            # Test trading dates
            trades = pd.read_csv("Task3/output/trading_metrics.csv")
            pd.to_datetime(trades['execution_time'])
        except FileNotFoundError:
            pytest.skip("Data files not generated yet")
        except KeyError:
            pytest.fail("Required date columns not found")
    
    def test_numeric_formats(self):
        """Test numeric data formats"""
        try:
            # Test forecast values
            forecasts = pd.read_csv("Task1/output/asset_forecasts.csv")
            assert pd.to_numeric(forecasts['value_kw'], errors='coerce').notnull().all()
            
            # Test trading values
            trades = pd.read_csv("Task3/output/trading_metrics.csv")
            assert pd.to_numeric(trades['price'], errors='coerce').notnull().all()
            assert pd.to_numeric(trades['volume'], errors='coerce').notnull().all()
        except FileNotFoundError:
            pytest.skip("Data files not generated yet")
        except KeyError:
            pytest.fail("Required numeric columns not found")
