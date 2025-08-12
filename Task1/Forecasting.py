# FlexPower Task 1: Asset and Portfolio Forecasting

import sys
sys.path.append('../DataEngineeringChallenge/DataEngineeringChallenge/src/')

import os
import pandas as pd
import pendulum
import json
# Import the actual VPP client
from vpp.client import get_forecast as vpp_get_forecast

def get_forecast(asset_id, version):
    #Get forecast data using the VPP client
    return vpp_get_forecast(
        asset_id=asset_id,
        version=version
    )

def extract_asset_ids(path):
    """
    Extract unique asset_id and entity_id from the 'key.asset_id' field
    inside each JSON file.
    """
    asset_ids = set()

    if not os.path.exists(path):
        print(f"ERROR Path does not exist: {path}")
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
                        if not asset_id: 
                            asset_id = entry.get("key", {}).get("entity_id")
                        if asset_id:
                            asset_ids.add(asset_id)

            except Exception as e:
                print(f"ERROR Failed to read {filename}: {e}")
    asset_ids = sorted(asset_ids)
    return asset_ids

def generate_intervals(day="2025-07-08"):
    start = pendulum.parse(day, tz="Europe/Berlin")
    intervals = [start.add(minutes=15 * i) for i in range(96)]
    return intervals

def fetch_latest_forecasts(asset_ids, intervals):
    all_forecasts = []
    for asset in asset_ids:
        print(asset)
        for interval in intervals:
            try:
                forecast = get_forecast(
                    asset_id=asset,
                    version=interval
                )
                if forecast:
                    all_forecasts.append(forecast)
            except Exception as e:
                print(e)
    return all_forecasts

def create_forecast_dataframes(all_forecasts):
    """Convert forecast data to DataFrames."""
    if not all_forecasts:
        return pd.DataFrame(), pd.DataFrame()
    
    all_records = []
    for forecast_json in all_forecasts:
        # Parse the JSON string
        forecast = json.loads(forecast_json)
        
        # Extract data
        asset_id = forecast['key']['asset_id']
        starts = pd.to_datetime(forecast['values'][0], unit='s')
        power_values = forecast['values'][3]
        
        # Create records
        for start, power in zip(starts, power_values):
            all_records.append({
                'delivery_start': start,
                'asset_id': asset_id,
                'value_kw': power
            })
    
    # Create DataFrame
    df_asset = pd.DataFrame(all_records)

    # Portfolio-level forecasts (sum all assets by delivery time)
    df_portfolio = df_asset.groupby('delivery_start')['value_kw'].sum().reset_index()
    df_portfolio.rename(columns={'value_kw': 'portfolio_forecast_kw'}, inplace=True)
    
    # print("Asset forecasts {len(df_asset)}")
    # print("Portfolio forecasts {len(df_portfolio)}")

    return df_asset, df_portfolio

def save_forecasts(df_asset, df_portfolio):
    os.makedirs("output", exist_ok=True)
    df_asset.to_csv("output/asset_forecasts.csv", index=False)
    df_portfolio.to_csv("output/portfolio_forecast.csv", index=False)


asset_dir = '../DataEngineeringChallenge/DataEngineeringChallenge/src/vpp/live_measured_infeed'

asset_ids = extract_asset_ids(asset_dir)
# print(asset_ids)
intervals = generate_intervals("2025-07-08")
# print(intervals)
forecasts = fetch_latest_forecasts(asset_ids, intervals)
# print(forecasts)
df_asset, df_portfolio = create_forecast_dataframes(forecasts)
# print(df_asset)
# print(df_portfolio)
save_forecasts(df_asset, df_portfolio)
