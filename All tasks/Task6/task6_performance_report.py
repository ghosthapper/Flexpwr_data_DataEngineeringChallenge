# task6_performance_report.py
# FlexPower Task 6: Performance Reporting - Main Code
# Takes input reference from Task 1 forecasting structure

import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

def load_forecast_data():
    """Load forecast data from Task 1 output or create mock data"""
    try:
        # Try to load actual forecast data from Task 1
        df_asset = pd.read_csv("output/asset_forecasts_20250608.csv")
        df_portfolio = pd.read_csv("output/portfolio_forecast_20250608.csv")
        print("[INFO] Loaded forecast data from Task 1")
        return df_asset, df_portfolio
    except FileNotFoundError:
        print("[INFO] Task 1 data not found, creating mock forecast data")
        # Create mock forecast data similar to Task 1 structure
        asset_ids = ['WF_001', 'WF_002', 'SF_001', 'SF_002']
        intervals = pd.date_range('2025-06-08 00:00:00', periods=96, freq='15T')
        
        forecasts = []
        for asset_id in asset_ids:
            for interval in intervals:
                forecasts.append({
                    'delivery_start': interval,
                    'asset_id': asset_id,
                    'value_kw': 1000 + hash(f"{asset_id}{interval}") % 500
                })
        
        df_asset = pd.DataFrame(forecasts)
        df_portfolio = df_asset.groupby('delivery_start')['value_kw'].sum().reset_index()
        df_portfolio.rename(columns={'value_kw': 'portfolio_forecast_kw'}, inplace=True)
        
        return df_asset, df_portfolio

def generate_actual_performance(df_asset):
    """Generate actual performance data based on forecast structure"""
    np.random.seed(42)
    
    # Asset info for realistic patterns
    asset_info = {
        'WF_001': {'name': 'Wind Farm Alpha', 'type': 'Wind', 'capacity_mw': 50},
        'WF_002': {'name': 'Wind Farm Beta', 'type': 'Wind', 'capacity_mw': 75},
        'SF_001': {'name': 'Solar Farm Gamma', 'type': 'Solar', 'capacity_mw': 30},
        'SF_002': {'name': 'Solar Farm Delta', 'type': 'Solar', 'capacity_mw': 45}
    }
    
    actuals = []
    for _, row in df_asset.iterrows():
        asset_id = row['asset_id']
        forecast_kw = row['value_kw']
        timestamp = pd.to_datetime(row['delivery_start'])
        hour = timestamp.hour
        
        # Add realistic variation to forecasts
        asset_type = asset_info.get(asset_id, {}).get('type', 'Wind')
        
        if asset_type == 'Solar':
            # Solar: lower at night, higher during day
            time_factor = max(0, np.sin((hour - 6) * np.pi / 12)) if 6 <= hour <= 18 else 0.1
            actual_factor = 0.7 + 0.4 * np.random.random()
        else:
            # Wind: more consistent but variable
            actual_factor = 0.8 + 0.4 * np.random.random()
        
        actual_kw = forecast_kw * actual_factor
        market_price = 45 + 25 * np.random.random()  # EUR/MWh
        
        # Convert kW to MWh for 15-minute intervals
        forecast_mwh = forecast_kw / 1000 * 0.25
        actual_mwh = actual_kw / 1000 * 0.25
        
        revenue = actual_mwh * market_price
        imbalance_cost = abs(forecast_mwh - actual_mwh) * 50  # Penalty per MWh deviation
        
        actuals.append({
            'asset_id': asset_id,
            'asset_name': asset_info.get(asset_id, {}).get('name', asset_id),
            'delivery_start': timestamp,
            'hour': hour,
            'forecast_kw': forecast_kw,
            'actual_kw': round(actual_kw, 2),
            'forecast_mwh': round(forecast_mwh, 4),
            'actual_mwh': round(actual_mwh, 4),
            'market_price_eur_mwh': round(market_price, 2),
            'revenue_eur': round(revenue, 2),
            'imbalance_cost_eur': round(imbalance_cost, 2),
            'net_revenue_eur': round(revenue - imbalance_cost, 2),
            'asset_type': asset_type,
            'capacity_mw': asset_info.get(asset_id, {}).get('capacity_mw', 0)
        })
    
    return pd.DataFrame(actuals)

def calculate_asset_metrics(df_performance):
    """Calculate key performance metrics for each asset"""
    metrics = []
    
    for asset_id in df_performance['asset_id'].unique():
        asset_data = df_performance[df_performance['asset_id'] == asset_id]
        
        # Basic metrics
        total_forecast = asset_data['forecast_mwh'].sum()
        total_actual = asset_data['actual_mwh'].sum()
        total_revenue = asset_data['revenue_eur'].sum()
        total_imbalance = asset_data['imbalance_cost_eur'].sum()
        net_revenue = asset_data['net_revenue_eur'].sum()
        
        # Performance indicators
        forecast_accuracy = (1 - abs(total_forecast - total_actual) / total_forecast) * 100 if total_forecast > 0 else 0
        capacity_mw = asset_data['capacity_mw'].iloc[0]
        capacity_factor = (total_actual / (capacity_mw * 24)) * 100 if capacity_mw > 0 else 0
        
        metrics.append({
            'asset_id': asset_id,
            'asset_name': asset_data['asset_name'].iloc[0],
            'asset_type': asset_data['asset_type'].iloc[0],
            'capacity_mw': capacity_mw,
            'total_forecast_mwh': round(total_forecast, 2),
            'total_actual_mwh': round(total_actual, 2),
            'forecast_accuracy_pct': round(forecast_accuracy, 1),
            'capacity_factor_pct': round(capacity_factor, 1),
            'total_revenue_eur': round(total_revenue, 2),
            'imbalance_cost_eur': round(total_imbalance, 2),
            'net_revenue_eur': round(net_revenue, 2)
        })
    
    return pd.DataFrame(metrics)

def calculate_portfolio_metrics(df_performance):
    """Calculate portfolio-level performance metrics"""
    total_forecast = df_performance['forecast_mwh'].sum()
    total_actual = df_performance['actual_mwh'].sum()
    total_revenue = df_performance['revenue_eur'].sum()
    total_imbalance = df_performance['imbalance_cost_eur'].sum()
    net_revenue = df_performance['net_revenue_eur'].sum()
    
    # Portfolio performance
    portfolio_accuracy = (1 - abs(total_forecast - total_actual) / total_forecast) * 100 if total_forecast > 0 else 0
    total_capacity = df_performance.groupby('asset_id')['capacity_mw'].first().sum()
    portfolio_capacity_factor = (total_actual / (total_capacity * 24)) * 100 if total_capacity > 0 else 0
    
    return {
        'total_assets': df_performance['asset_id'].nunique(),
        'total_capacity_mw': total_capacity,
        'total_forecast_mwh': round(total_forecast, 2),
        'total_actual_mwh': round(total_actual, 2),
        'portfolio_accuracy_pct': round(portfolio_accuracy, 1),
        'portfolio_capacity_factor_pct': round(portfolio_capacity_factor, 1),
        'total_revenue_eur': round(total_revenue, 2),
        'total_imbalance_cost_eur': round(total_imbalance, 2),
        'net_revenue_eur': round(net_revenue, 2),
        'avg_market_price': round(df_performance['market_price_eur_mwh'].mean(), 2)
    }

def create_performance_report(asset_metrics, portfolio_metrics):
    """Generate text-based performance report"""
    report = []
    report.append("=" * 80)
    report.append("FLEXPOWER PORTFOLIO PERFORMANCE REPORT")
    report.append("=" * 80)
    report.append(f"Delivery Date: 2025-06-08")
    report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Portfolio Summary
    report.append("PORTFOLIO OVERVIEW")
    report.append("-" * 40)
    report.append(f"Total Assets: {portfolio_metrics['total_assets']}")
    report.append(f"Total Capacity: {portfolio_metrics['total_capacity_mw']} MW")
    report.append(f"Total Production: {portfolio_metrics['total_actual_mwh']} MWh")
    report.append(f"Portfolio Capacity Factor: {portfolio_metrics['portfolio_capacity_factor_pct']}%")
    report.append(f"Portfolio Forecast Accuracy: {portfolio_metrics['portfolio_accuracy_pct']}%")
    report.append("")
    
    # Financial Performance
    report.append("FINANCIAL PERFORMANCE")
    report.append("-" * 40)
    report.append(f"Total Revenue: €{portfolio_metrics['total_revenue_eur']:,.2f}")
    report.append(f"Total Imbalance Costs: €{portfolio_metrics['total_imbalance_cost_eur']:,.2f}")
    report.append(f"Net Revenue: €{portfolio_metrics['net_revenue_eur']:,.2f}")
    report.append(f"Average Market Price: €{portfolio_metrics['avg_market_price']:.2f}/MWh")
    report.append("")
    
    # Individual Asset Performance
    report.append("INDIVIDUAL ASSET PERFORMANCE")
    report.append("-" * 80)
    for _, asset in asset_metrics.iterrows():
        report.append(f"\n{asset['asset_name']} ({asset['asset_id']})")
        report.append(f"  Type: {asset['asset_type']} | Capacity: {asset['capacity_mw']} MW")
        report.append(f"  Production: {asset['total_actual_mwh']} MWh")
        report.append(f"  Capacity Factor: {asset['capacity_factor_pct']}%")
        report.append(f"  Forecast Accuracy: {asset['forecast_accuracy_pct']}%")
        report.append(f"  Revenue: €{asset['total_revenue_eur']:,.2f}")
        report.append(f"  Imbalance Cost: €{asset['imbalance_cost_eur']:,.2f}")
        report.append(f"  Net Revenue: €{asset['net_revenue_eur']:,.2f}")
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)

def save_results(df_performance, asset_metrics, portfolio_metrics, report_text):
    """Save all results to files"""
    os.makedirs("output", exist_ok=True)
    
    # Save performance data
    df_performance.to_csv("output/performance_data_20250608.csv", index=False)
    print("[INFO] Saved performance_data_20250608.csv")
    
    # Save asset metrics
    asset_metrics.to_csv("output/asset_metrics_20250608.csv", index=False)
    print("[INFO] Saved asset_metrics_20250608.csv")
    
    # Save portfolio metrics as JSON
    with open("output/portfolio_metrics_20250608.json", "w") as f:
        json.dump(portfolio_metrics, f, indent=2)
    print("[INFO] Saved portfolio_metrics_20250608.json")
    
    # Save report
    with open("output/performance_report_20250608.txt", "w") as f:
        f.write(report_text)
    print("[INFO] Saved performance_report_20250608.txt")

def main():
    """Main function to run Task 6 performance reporting"""
    print("FlexPower Task 6: Performance Reporting")
    print("=" * 50)
    
    # Step 1: Load forecast data from Task 1
    print("1. Loading forecast data from Task 1...")
    df_asset_forecast, df_portfolio_forecast = load_forecast_data()
    
    # Step 2: Generate actual performance data
    print("2. Generating actual performance data...")
    df_performance = generate_actual_performance(df_asset_forecast)
    
    # Step 3: Calculate asset metrics
    print("3. Calculating asset performance metrics...")
    asset_metrics = calculate_asset_metrics(df_performance)
    
    # Step 4: Calculate portfolio metrics
    print("4. Calculating portfolio metrics...")
    portfolio_metrics = calculate_portfolio_metrics(df_performance)
    
    # Step 5: Generate performance report
    print("5. Generating performance report...")
    report_text = create_performance_report(asset_metrics, portfolio_metrics)
    
    # Step 6: Save all results
    print("6. Saving results...")
    save_results(df_performance, asset_metrics, portfolio_metrics, report_text)
    
    print("\n" + "=" * 80)
    print("PERFORMANCE REPORT COMPLETED!")
    print("=" * 80)
    print(report_text)
    
    print(f"\nFiles saved to ./output/:")
    print("- performance_data_20250608.csv")
    print("- asset_metrics_20250608.csv") 
    print("- portfolio_metrics_20250608.json")
    print("- performance_report_20250608.txt")
    
    return df_performance, asset_metrics, portfolio_metrics

if __name__ == "__main__":
    main()