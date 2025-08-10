# FlexPower Task 2: Best-of-Infeed Analysis
# This script computes best-of-infeed on asset level and portfolio aggregation

import os
import pandas as pd
import json
from datetime import datetime, timedelta
import numpy as np

def extract_asset_ids(path):
    """Extract unique asset IDs from JSON files"""
    asset_ids = set()
    
    if not os.path.exists(path):
        print(f"[ERROR] Path does not exist: {path}")
        return []
    
    for filename in os.listdir(path):
        if filename.endswith('.json'):
            filepath = os.path.join(path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    records = data if isinstance(data, list) else [data]
                    
                    for entry in records:
                        asset_id = entry.get("key", {}).get("asset_id")
                        if asset_id:
                            asset_ids.add(asset_id)
                            
            except Exception as e:
                print(f"[ERROR] Failed to read {filename}: {e}")
    
    asset_ids = sorted(asset_ids)
    print(f"[INFO] Found {len(asset_ids)} assets for best-of-infeed analysis")
    return asset_ids

def load_live_measured_data(asset_dir):
    """Load live measured infeed data from JSON files"""
    all_data = []
    
    for filename in os.listdir(asset_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(asset_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    records = data if isinstance(data, list) else [data]
                    
                    for entry in records:
                        key = entry.get("key", {})
                        value = entry.get("value", {})
                        
                        all_data.append({
                            'asset_id': key.get("asset_id"),
                            'delivery_start': key.get("delivery_start"),
                            'measured_kw': value.get("value_kw", 0),
                            'timestamp': value.get("timestamp")
                        })
                        
            except Exception as e:
                print(f"[ERROR] Failed to read {filename}: {e}")
    
    df = pd.DataFrame(all_data)
    if not df.empty:
        df['delivery_start'] = pd.to_datetime(df['delivery_start'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print(f"[INFO] Loaded {len(df)} live measured records")
    return df

def load_forecast_data():
    """Load forecast data for comparison"""
    try:
        df_forecast = pd.read_csv("../Task1/output/asset_forecasts_20250608.csv")
        df_forecast['delivery_start'] = pd.to_datetime(df_forecast['delivery_start'])
        print(f"[INFO] Loaded {len(df_forecast)} forecast records")
        return df_forecast
    except FileNotFoundError:
        print("[WARNING] Forecast data not found. Run Task 1 first for complete analysis.")
        return pd.DataFrame()

def compute_best_of_infeed_asset_level(df_measured, df_forecast):
    """Compute best-of-infeed for each asset"""
    
    if df_forecast.empty:
        # If no forecast data, use measured data only
        best_of_infeed = df_measured.groupby(['asset_id', 'delivery_start']).agg({
            'measured_kw': 'max'  # Take maximum measured value
        }).reset_index()
        best_of_infeed['forecast_kw'] = 0
        best_of_infeed['best_of_infeed_kw'] = best_of_infeed['measured_kw']
    else:
        # Merge forecast and measured data
        merged = pd.merge(
            df_forecast, 
            df_measured.groupby(['asset_id', 'delivery_start'])['measured_kw'].max().reset_index(),
            on=['asset_id', 'delivery_start'],
            how='outer'
        )
        
        # Fill missing values with 0
        merged['measured_kw'] = merged['measured_kw'].fillna(0)
        merged['value_kw'] = merged['value_kw'].fillna(0)
        
        # Convert to numeric to avoid dtype issues
        merged['measured_kw'] = pd.to_numeric(merged['measured_kw'], errors='coerce').fillna(0)
        merged['value_kw'] = pd.to_numeric(merged['value_kw'], errors='coerce').fillna(0)
        
        # Best-of-infeed: take maximum between forecast and measured
        merged['best_of_infeed_kw'] = np.maximum(merged['value_kw'], merged['measured_kw'])
        
        best_of_infeed = merged[['asset_id', 'delivery_start', 'value_kw', 'measured_kw', 'best_of_infeed_kw']].copy()
        best_of_infeed.rename(columns={'value_kw': 'forecast_kw'}, inplace=True)
    
    # Ensure numeric columns are properly typed
    numeric_cols = ['forecast_kw', 'measured_kw', 'best_of_infeed_kw']
    for col in numeric_cols:
        if col in best_of_infeed.columns:
            best_of_infeed[col] = pd.to_numeric(best_of_infeed[col], errors='coerce').fillna(0)
    
    print(f"[INFO] Computed best-of-infeed for {best_of_infeed['asset_id'].nunique()} assets")
    return best_of_infeed

def compute_portfolio_best_of_infeed(df_asset_best_of_infeed):
    """Aggregate best-of-infeed to portfolio level"""
    
    portfolio_best_of_infeed = df_asset_best_of_infeed.groupby('delivery_start').agg({
        'forecast_kw': 'sum',
        'measured_kw': 'sum', 
        'best_of_infeed_kw': 'sum'
    }).reset_index()
    
    portfolio_best_of_infeed.rename(columns={
        'forecast_kw': 'portfolio_forecast_kw',
        'measured_kw': 'portfolio_measured_kw',
        'best_of_infeed_kw': 'portfolio_best_of_infeed_kw'
    }, inplace=True)
    
    print(f"[INFO] Computed portfolio best-of-infeed for {len(portfolio_best_of_infeed)} time intervals")
    return portfolio_best_of_infeed

def calculate_best_of_infeed_metrics(df_asset, df_portfolio):
    """Calculate key metrics for best-of-infeed analysis"""
    
    metrics = {}
    
    # Asset level metrics
    total_assets = df_asset['asset_id'].nunique()
    avg_best_of_infeed = df_asset['best_of_infeed_kw'].mean()
    max_asset_performance = df_asset.groupby('asset_id')['best_of_infeed_kw'].max().max()
    
    # Portfolio level metrics  
    portfolio_peak = df_portfolio['portfolio_best_of_infeed_kw'].max()
    portfolio_avg = df_portfolio['portfolio_best_of_infeed_kw'].mean()
    
    # Compare forecast vs best-of-infeed (if forecast data exists)
    if 'portfolio_forecast_kw' in df_portfolio.columns:
        forecast_accuracy = (
            df_portfolio['portfolio_forecast_kw'].sum() / 
            df_portfolio['portfolio_best_of_infeed_kw'].sum() * 100
        )
        metrics['forecast_accuracy'] = forecast_accuracy
    
    metrics.update({
        'total_assets': total_assets,
        'avg_best_of_infeed_kw': avg_best_of_infeed,
        'max_asset_performance_kw': max_asset_performance,
        'portfolio_peak_kw': portfolio_peak,
        'portfolio_avg_kw': portfolio_avg
    })
    
    return metrics

def save_best_of_infeed_data(df_asset, df_portfolio, metrics):
    """Save best-of-infeed results to CSV files"""
    
    os.makedirs("output", exist_ok=True)
    
    # Save data
    df_asset.to_csv("output/asset_best_of_infeed_20250608.csv", index=False)
    df_portfolio.to_csv("output/portfolio_best_of_infeed_20250608.csv", index=False)
    
    # Save metrics
    with open("output/best_of_infeed_metrics.json", 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("[INFO] Saved best-of-infeed data and metrics to output/ directory")

def main():
    """Main function for Task 2: Best-of-Infeed Analysis"""
    
    print("FlexPower Task 2: Best-of-Infeed Analysis")
    print("=" * 50)
    
    # Data directories
    live_measured_dir = "../DataEngineeringChallenge-main/DataEngineeringChallenge-main/src/vpp/live_measured_infeed"
    
    # Step 1: Load live measured data
    print("\n📊 Loading live measured data...")
    df_measured = load_live_measured_data(live_measured_dir)
    
    # print(df_measured)
    
    # Step 2: Load forecast data (from Task 1)
    print("\n📈 Loading forecast data...")
    df_forecast = load_forecast_data()
    
    print(df_forecast)
    # Step 3: Compute asset-level best-of-infeed
    print("\n🏭 Computing asset-level best-of-infeed...")
    df_asset_best_of_infeed = compute_best_of_infeed_asset_level(df_measured, df_forecast)
    
    # Step 4: Compute portfolio-level best-of-infeed
    print("\n📊 Computing portfolio-level best-of-infeed...")
    df_portfolio_best_of_infeed = compute_portfolio_best_of_infeed(df_asset_best_of_infeed)
    
    # Step 5: Calculate metrics
    print("\n📋 Calculating best-of-infeed metrics...")
    metrics = calculate_best_of_infeed_metrics(df_asset_best_of_infeed, df_portfolio_best_of_infeed)
    
    # Step 6: Save results
    print("\n💾 Saving results...")
    save_best_of_infeed_data(df_asset_best_of_infeed, df_portfolio_best_of_infeed, metrics)
    
    # Print summary
    print(f"\n✅ Task 2 Complete - Best-of-Infeed Analysis")
    print(f"   • Assets analyzed: {metrics['total_assets']}")
    print(f"   • Portfolio peak: {metrics['portfolio_peak_kw']/1000:.1f} MW")
    print(f"   • Portfolio average: {metrics['portfolio_avg_kw']/1000:.1f} MW")
    
    if 'forecast_accuracy' in metrics:
        print(f"   • Forecast accuracy: {metrics['forecast_accuracy']:.1f}%")

if __name__ == "__main__":
    main()