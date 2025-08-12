import sys
import os
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_forecast_data_structure():
    """Test that forecast data has the correct structure"""
    try:
        df = pd.read_csv("Task1/output/asset_forecasts.csv")
        required_columns = ['delivery_start', 'asset_id', 'value_kw']
        assert all(col in df.columns for col in required_columns)
        assert not df.empty
    except FileNotFoundError:
        pytest.skip("Forecast data not generated yet")

def test_best_of_infeed_metrics():
    """Test that best-of-infeed metrics are valid"""
    try:
        import json
        with open("Task2/output/best_of_infeed_metrics.json", 'r') as f:
            metrics = json.load(f)
        
        assert 'forecast_accuracy' in metrics
        assert 'total_assets' in metrics
        assert metrics['forecast_accuracy'] >= 0
        assert metrics['total_assets'] > 0
    except FileNotFoundError:
        pytest.skip("Best-of-infeed metrics not generated yet")

def test_trading_data():
    """Test trading data validity"""
    try:
        trades = pd.read_csv("Task3/output/trading_metrics.csv")
        assert 'volume' in trades.columns
        assert 'price' in trades.columns
        assert (trades['volume'] >= 0).all()
        assert (trades['price'] >= 0).all()
    except FileNotFoundError:
        pytest.skip("Trading data not generated yet")

def test_invoice_generation():
    """Test invoice generation"""
    try:
        import glob
        invoice_files = glob.glob("Task5/output/invoice_*.json")
        assert len(invoice_files) > 0
        
        with open(invoice_files[0], 'r') as f:
            invoice = json.load(f)
        assert 'invoice_number' in invoice
        assert 'total_amount' in invoice
        assert float(invoice['total_amount']) >= 0
    except (FileNotFoundError, IndexError):
        pytest.skip("Invoice files not generated yet")

def test_performance_report():
    """Test performance report generation"""
    try:
        with open("Task6/output/portfolio_metrics_20250608.json", 'r') as f:
            metrics = json.load(f)
        assert 'portfolio_capacity' in metrics
        assert 'total_production' in metrics
        assert metrics['portfolio_capacity'] > 0
    except FileNotFoundError:
        pytest.skip("Performance report not generated yet")
