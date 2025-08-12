# task6_performance_report.py

import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

def load_forecast_data():
    # Load forecast data from Task 2's best-of-infeed output
    try:
        # Load actual + forecast data from Task 2
        df = pd.read_csv("../Task2/output/asset_best_of_infeed.csv")
        df['delivery_start'] = pd.to_datetime(df['delivery_start'])
        
        # Create asset forecasts
        df_asset = df[['asset_id', 'delivery_start', 'forecast_kw']].copy()
        df_asset.rename(columns={'forecast_kw': 'value_kw'}, inplace=True)
        
        # Create portfolio forecasts
        df_portfolio = df.groupby('delivery_start')['forecast_kw'].sum().reset_index()
        df_portfolio.rename(columns={'forecast_kw': 'portfolio_forecast_kw'}, inplace=True)
        
        if df_asset.empty or df_portfolio.empty:
            raise FileNotFoundError("No forecast data found")
            
        return df_asset, df_portfolio
        
    except Exception as e:
        print(f"Could not load forecast data: {e}")
        raise

def load_asset_info():
    # Load actual asset information from VPP data
    asset_info = {}
    base_path = "../DataEngineeringChallenge/DataEngineeringChallenge/src/vpp/technical_data"
    
    try:
        for file in os.listdir(base_path):
            if file.endswith('.json'):
                with open(os.path.join(base_path, file)) as f:
                    data = json.load(f)
                    for asset in data.get('assets', []):
                        asset_id = asset.get('asset_id')
                        tech_attrs = asset.get('technical_attributes', {})
                        if asset_id:
                            asset_type = 'Wind' if 'WND' in asset_id else 'Solar'
                            name = f"{asset_type} Farm {asset_id}"
                            asset_info[asset_id] = {
                                'name': name,
                                'type': asset_type,
                                'capacity_mw': tech_attrs.get('capacity_kw', 0) / 1000  # Convert kW to MW
                            }
    except Exception as e:
        print(f"[ERROR] Could not load asset info: {e}")
        raise
    
    return asset_info

def get_market_prices():
    """Load or simulate market prices"""
    default_price = 50.0  # Default market price in EUR/MWh
    
    try:
        # Try to load trading data from Task 3
        trading_data = pd.read_csv("../Task3/output/trading_data.csv")
        if not trading_data.empty:
            trading_data['delivery_start'] = pd.to_datetime(trading_data['DeliveryStart'])
            prices = trading_data.groupby('delivery_start')['Price'].mean().reset_index()
            prices.columns = ['delivery_start', 'price']
            return prices, True
    except Exception as e:
        print(f"[WARNING] Could not load trading data: {e}")
    
    print("[INFO] Using default market price")
    return pd.DataFrame({'price': [default_price]}), False

def generate_actual_performance(df_asset):
    """Generate performance data using actual data sources - OPTIMIZED"""
    # Load asset information
    asset_info = load_asset_info()
    
    # Load actual production data from Task 2
    try:
        actual_data = pd.read_csv("../Task2/output/asset_best_of_infeed.csv")
        actual_data['delivery_start'] = pd.to_datetime(actual_data['delivery_start'])
        # Create a more efficient lookup using merge instead of set_index
        actual_lookup = actual_data[['asset_id', 'delivery_start', 'best_of_infeed_kw']].copy()
    except FileNotFoundError as e:
        print(f"[ERROR] Could not load actual production data: {e}")
        raise
        
    # Load market prices from Task 3 or use default
    market_prices, using_actual_prices = get_market_prices()
    print(f"[INFO] Using {'actual' if using_actual_prices else 'default'} market prices")
    market_price = market_prices['price'].iloc[0]
    
    # Merge forecast data with actual data for efficient lookup
    df_merged = df_asset.merge(
        actual_lookup, 
        on=['asset_id', 'delivery_start'], 
        how='left'
    )
    
    # Fill missing actual values with 0
    df_merged['best_of_infeed_kw'] = df_merged['best_of_infeed_kw'].fillna(0)
    
    # Vectorized calculations instead of row-by-row processing
    df_merged['forecast_mwh'] = df_merged['value_kw'] / 1000 * 0.25
    df_merged['actual_mwh'] = df_merged['best_of_infeed_kw'] / 1000 * 0.25
    df_merged['revenue_eur'] = df_merged['actual_mwh'] * market_price
    df_merged['imbalance_cost_eur'] = abs(df_merged['forecast_mwh'] - df_merged['actual_mwh']) * 50
    df_merged['net_revenue_eur'] = df_merged['revenue_eur'] - df_merged['imbalance_cost_eur']
    
    # Add asset information efficiently
    asset_info_df = pd.DataFrame.from_dict(asset_info, orient='index').reset_index()
    asset_info_df.columns = ['asset_id', 'name', 'type', 'capacity_mw']
    
    df_final = df_merged.merge(asset_info_df, on='asset_id', how='left')
    
    # Fill missing asset info
    df_final['name'] = df_final['name'].fillna(df_final['asset_id'])
    df_final['type'] = df_final['type'].fillna(
        df_final['asset_id'].apply(lambda x: 'Wind' if 'WND' in str(x) else 'Solar')
    )
    df_final['capacity_mw'] = df_final['capacity_mw'].fillna(0)
    
    # Create final dataframe with required columns
    result_df = pd.DataFrame({
        'asset_id': df_final['asset_id'],
        'asset_name': df_final['name'],
        'delivery_start': df_final['delivery_start'],
        'hour': df_final['delivery_start'].dt.hour,
        'forecast_kw': df_final['value_kw'],
        'actual_kw': df_final['best_of_infeed_kw'].round(2),
        'forecast_mwh': df_final['forecast_mwh'].round(4),
        'actual_mwh': df_final['actual_mwh'].round(4),
        'market_price_eur_mwh': round(market_price, 2),
        'revenue_eur': df_final['revenue_eur'].round(2),
        'imbalance_cost_eur': df_final['imbalance_cost_eur'].round(2),
        'net_revenue_eur': df_final['net_revenue_eur'].round(2),
        'asset_type': df_final['type'],
        'capacity_mw': df_final['capacity_mw']
    })
    
    return result_df

def calculate_asset_metrics(df_performance):
    """Calculate key performance metrics for each asset - OPTIMIZED"""
    # Group by asset_id and calculate all metrics at once using vectorized operations
    grouped = df_performance.groupby('asset_id').agg({
        'asset_name': 'first',
        'asset_type': 'first',
        'capacity_mw': 'first',
        'forecast_mwh': 'sum',
        'actual_mwh': 'sum',
        'revenue_eur': 'sum',
        'imbalance_cost_eur': 'sum',
        'net_revenue_eur': 'sum'
    }).reset_index()
    
    # Vectorized calculations for performance indicators
    grouped['forecast_accuracy_pct'] = np.where(
        grouped['forecast_mwh'] > 0,
        (1 - abs(grouped['forecast_mwh'] - grouped['actual_mwh']) / grouped['forecast_mwh']) * 100,
        0
    ).round(1)
    
    grouped['capacity_factor_pct'] = np.where(
        grouped['capacity_mw'] > 0,
        (grouped['actual_mwh'] / (grouped['capacity_mw'] * 24)) * 100,
        0
    ).round(1)
    
    # Rename columns to match expected output
    grouped.rename(columns={
        'forecast_mwh': 'total_forecast_mwh',
        'actual_mwh': 'total_actual_mwh',
        'revenue_eur': 'total_revenue_eur'
    }, inplace=True)
    
    # Round numeric columns
    numeric_cols = ['total_forecast_mwh', 'total_actual_mwh', 'total_revenue_eur', 
                   'imbalance_cost_eur', 'net_revenue_eur']
    grouped[numeric_cols] = grouped[numeric_cols].round(2)
    
    return grouped

def calculate_portfolio_metrics(df_performance):
    """Calculate portfolio-level performance metrics - HEAVILY OPTIMIZED"""
    # Use vectorized operations for all calculations
    total_forecast = df_performance['forecast_mwh'].sum()
    total_actual = df_performance['actual_mwh'].sum()
    total_revenue = df_performance['revenue_eur'].sum()
    total_imbalance = df_performance['imbalance_cost_eur'].sum()
    net_revenue = df_performance['net_revenue_eur'].sum()
    
    # Portfolio performance
    portfolio_accuracy = (1 - abs(total_forecast - total_actual) / total_forecast) * 100 if total_forecast > 0 else 0
    
    # More efficient capacity calculation - avoid groupby on large dataset
    total_capacity = df_performance.drop_duplicates('asset_id')['capacity_mw'].sum()
    portfolio_capacity_factor = (total_actual / (total_capacity * 24)) * 100 if total_capacity > 0 else 0
    
    # Count unique assets efficiently
    total_assets = df_performance['asset_id'].nunique()
    
    # Average market price (should be constant anyway)
    avg_market_price = df_performance['market_price_eur_mwh'].iloc[0]  # More efficient than mean()
    
    return {
        'total_assets': total_assets,
        'total_capacity_mw': total_capacity,
        'total_forecast_mwh': round(total_forecast, 2),
        'total_actual_mwh': round(total_actual, 2),
        'portfolio_accuracy_pct': round(portfolio_accuracy, 1),
        'portfolio_capacity_factor_pct': round(portfolio_capacity_factor, 1),
        'total_revenue_eur': round(total_revenue, 2),
        'total_imbalance_cost_eur': round(total_imbalance, 2),
        'net_revenue_eur': round(net_revenue, 2),
        'avg_market_price': round(avg_market_price, 2)
    }

def create_performance_report(asset_metrics, portfolio_metrics):
    """Generate text-based performance report - OPTIMIZED"""
    # Use list comprehension and join for better performance
    lines = [
        "=" * 80,
        "FLEXPOWER PORTFOLIO PERFORMANCE REPORT",
        "=" * 80,
        f"Delivery Date: 2025-06-08",
        f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "PORTFOLIO OVERVIEW",
        "-" * 40,
        f"Total Assets: {portfolio_metrics['total_assets']}",
        f"Total Capacity: {portfolio_metrics['total_capacity_mw']} MW",
        f"Total Production: {portfolio_metrics['total_actual_mwh']} MWh",
        f"Portfolio Capacity Factor: {portfolio_metrics['portfolio_capacity_factor_pct']}%",
        f"Portfolio Forecast Accuracy: {portfolio_metrics['portfolio_accuracy_pct']}%",
        "",
        "FINANCIAL PERFORMANCE",
        "-" * 40,
        f"Total Revenue: €{portfolio_metrics['total_revenue_eur']:,.2f}",
        f"Total Imbalance Costs: €{portfolio_metrics['total_imbalance_cost_eur']:,.2f}",
        f"Net Revenue: €{portfolio_metrics['net_revenue_eur']:,.2f}",
        f"Average Market Price: €{portfolio_metrics['avg_market_price']:.2f}/MWh",
        "",
        "INDIVIDUAL ASSET PERFORMANCE",
        "-" * 80
    ]
    
    # More efficient asset processing
    for _, asset in asset_metrics.iterrows():
        lines.extend([
            f"\n{asset['asset_name']} ({asset['asset_id']})",
            f"  Type: {asset['asset_type']} | Capacity: {asset['capacity_mw']} MW",
            f"  Production: {asset['total_actual_mwh']} MWh",
            f"  Capacity Factor: {asset['capacity_factor_pct']}%",
            f"  Forecast Accuracy: {asset['forecast_accuracy_pct']}%",
            f"  Revenue: €{asset['total_revenue_eur']:,.2f}",
            f"  Imbalance Cost: €{asset['imbalance_cost_eur']:,.2f}",
            f"  Net Revenue: €{asset['net_revenue_eur']:,.2f}"
        ])
    
    lines.extend(["", "=" * 80])
    
    return "\n".join(lines)

def save_results(df_performance, asset_metrics, portfolio_metrics, report_text):
    """Save all results to files"""
    # Clean up old files
    output_dir = "output"
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error: {e}")
    else:
        os.makedirs(output_dir)
    
    # Save performance data
    df_performance.to_csv("output/performance_data.csv", index=False)
    print("[INFO] Saved performance_data.csv")
    
    # Save asset metrics
    asset_metrics.to_csv("output/asset_metrics.csv", index=False)
    print("[INFO] Saved asset_metrics.csv")
    
    # Save portfolio metrics as JSON
    with open("output/portfolio_metrics.json", "w") as f:
        # Convert numpy types to native Python types
        portfolio_metrics_json = {k: float(v) if isinstance(v, (np.float64, np.float32, np.int64, np.int32)) else v 
                                for k, v in portfolio_metrics.items()}
        json.dump(portfolio_metrics_json, f, indent=2)
    print("[INFO] Saved portfolio_metrics.json")
    
    # Save report
    with open("output/performance_report.txt", "w") as f:
        f.write(report_text)
    print("[INFO] Saved performance_report.txt")

def main():
    
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
    
    return df_performance, asset_metrics, portfolio_metrics

if __name__ == "__main__":
    main()