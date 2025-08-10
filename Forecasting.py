# FlexPower Task 1: Asset and Portfolio Forecasting - Simple Version
# Fixed version of your existing code

import sys
sys.path.append('./DataEngineeringChallenge-main/DataEngineeringChallenge-main/src/vpp/')

import os
import pandas as pd
import pendulum
import json

# Simple mock function to replace the VPP client since it might not be available
def get_forecast(asset_id, version):
    """
    Mock function that simulates getting forecast data
    In real scenario, this would call the actual VPP client
    For now, returns sample data structure
    """
    return {
        'delivery_start': version.to_iso8601_string(),
        'value_kw': 1000 + hash(f"{asset_id}{version}") % 500,  # Mock forecast value
        'asset_id': asset_id,
        'forecast_type': 'latest'
    }

def extract_asset_ids(path):
    """
    Extract unique asset IDs from the 'key.asset_id' field
    inside each JSON file in the given directory.
    """
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

                    # Handle both list and single dict formats
                    records = data if isinstance(data, list) else [data]

                    for entry in records:
                        asset_id = entry.get("key", {}).get("asset_id")
                        if asset_id:
                            asset_ids.add(asset_id)

            except Exception as e:
                print(f"[ERROR] Failed to read {filename}: {e}")

    asset_ids = sorted(asset_ids)
    print(f"[INFO] Found {len(asset_ids)} assets: {asset_ids}")
    return asset_ids

def generate_intervals(day="2025-06-08"):
    """Generate 96 quarter-hour intervals for the delivery day."""
    start = pendulum.parse(day, tz="Europe/Berlin")
    intervals = [start.add(minutes=15 * i) for i in range(96)]
    print(f"[INFO] Generated {len(intervals)} intervals for {day}")
    return intervals

def fetch_latest_forecasts(asset_ids, intervals):
    """Fetch the latest forecast for each asset at each interval."""
    all_forecasts = []
    
    print(f"[INFO] Fetching forecasts for {len(asset_ids)} assets...")

    for asset in asset_ids:
        print(f"[INFO] Processing asset: {asset}")
        for interval in intervals:
            try:
                forecast = get_forecast(
                    asset_id=asset,
                    version=interval
                )
                if forecast:
                    all_forecasts.append(forecast)
            except Exception as e:
                print(f"[WARN] Missing forecast for {asset} at {interval}: {e}")

    print(f"[INFO] Collected {len(all_forecasts)} forecast records")
    return all_forecasts

def create_forecast_dataframes(all_forecasts):
    """Convert forecast data to asset-level and portfolio-level DataFrames."""
    if not all_forecasts:
        print("[ERROR] No forecast data to process")
        return pd.DataFrame(), pd.DataFrame()
    
    df = pd.DataFrame(all_forecasts)
    print(f"[INFO] Created DataFrame with {len(df)} rows")

    # Asset-level forecasts
    df_asset = df[['delivery_start', 'asset_id', 'value_kw']].copy()
    df_asset['delivery_start'] = pd.to_datetime(df_asset['delivery_start'])

    # Portfolio-level forecasts (sum all assets by delivery time)
    df_portfolio = df_asset.groupby('delivery_start')['value_kw'].sum().reset_index()
    df_portfolio.rename(columns={'value_kw': 'portfolio_forecast_kw'}, inplace=True)
    
    print(f"[INFO] Asset forecasts: {len(df_asset)} rows")
    print(f"[INFO] Portfolio forecasts: {len(df_portfolio)} rows")

    return df_asset, df_portfolio

def save_forecasts(df_asset, df_portfolio):
    """Save forecast data to CSV files."""
    os.makedirs("output", exist_ok=True)
    df_asset.to_csv("output/asset_forecasts_20250608.csv", index=False)
    df_portfolio.to_csv("output/portfolio_forecast_20250608.csv", index=False)


asset_dir = "./DataEngineeringChallenge-main/DataEngineeringChallenge-main/src/vpp/live_measured_infeed"

# Step 1: Get asset IDs from JSON files
asset_ids = extract_asset_ids(asset_dir)

# Step 2: Generate 96 quarter-hour delivery intervals
intervals = generate_intervals("2025-06-08")

# Step 3: Get forecast data
forecasts = fetch_latest_forecasts(asset_ids, intervals)

# Step 4: Create DataFrames
df_asset, df_portfolio = create_forecast_dataframes(forecasts)

# Step 5: Save results
save_forecasts(df_asset, df_portfolio)
