# FlexPower Task 2: Best-of-Infeed Analysis

import os
import pandas as pd
import json
from datetime import datetime, timedelta
import numpy as np

def extract_asset_ids(path):
    """Extract unique asset IDs from JSON files"""
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
                    
                    records = data if isinstance(data, list) else [data]
                    
                    for entry in records:
                        asset_id = entry.get("key", {}).get("asset_id")
                        if asset_id:
                            asset_ids.add(asset_id)
                            
            except Exception as e:
                print(e)
    
    asset_ids = sorted(asset_ids)
    return asset_ids

def load_live_measured_data(asset_dir):
    "Load live measured infeed data from JSON files"
    if not os.path.exists(asset_dir):
        print(f"ERROR Directory not found: {asset_dir}")
        return pd.DataFrame()
    all_data = []
    
    for filename in os.listdir(asset_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(asset_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        continue

                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError as e:
                        print(f"[WARNING] Invalid JSON in file:{e}")
                        continue

                    if not data:
                        print(f"[WARNING] No data in file: {filename}")
                        continue

                    # Extract asset information
                    asset_id = data.get('key', {}).get('asset_id') or data.get('key', {}).get('entity_id')
                    if not asset_id:
                        print(f"[WARNING] No asset_id in file: {filename}")
                        continue

                    asset_type = 'WND' if 'WND' in asset_id else 'SOL' if 'SOL' in asset_id else 'UNKNOWN'

                    # Get measurement data arrays
                    values_array = data.get('values', [])
                    if len(values_array) < 2:
                        print(f"[WARNING] Insufficient values arrays in file: {filename}")
                        continue

                    timestamps = values_array[0]  # First array contains timestamps in milliseconds
                    values = values_array[1]      # Second array contains measured values in kW

                    if not timestamps or not values:
                        print(f"[WARNING] Empty timestamps or values in file: {filename}")
                        continue

                    if len(timestamps) != len(values):
                        print(f"[WARNING] Mismatched timestamps and values lengths in file: {filename}")
                        continue
                    
                    # Process measurements
                    if len(timestamps) == len(values):
                        for ts, val in zip(timestamps, values):
                            # Convert milliseconds timestamp to datetime in Europe/Berlin timezone
                            delivery_start = pd.Timestamp(ts, unit='ms', tz='UTC').tz_convert('Europe/Berlin')
                            
                            # Filter out invalid measurements
                            if val >= 0:  # Only use non-negative values
                                all_data.append({
                                    'asset_id': asset_id,
                                    'asset_type': asset_type,
                                    'delivery_start': delivery_start,
                                    'measured_kw': float(val),
                                    'timestamp': delivery_start
                                })
                        
            except Exception as e:
                print(f"ERROR Failed to read {filename}: {e}")
                
    df = pd.DataFrame(all_data)
    if not df.empty:
        # print(df.shape)
        # print(df['delivery_start'].head())
        # print(df['measured_kw'].head())
        
        # Ensure consistent timezone handling
        df['delivery_start'] = pd.to_datetime(df['delivery_start'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        print(df['delivery_start'].head())
        
        # Group by 15-minute intervals to match forecast data format
        # Use mean for regular power measurements (kW)
        df['delivery_start'] = df['delivery_start'].dt.floor('15min')
        
        print(df['delivery_start'].head())
        
        # First calculate the mean and count
        agg_df = df.groupby(['asset_id', 'asset_type', 'delivery_start']).agg({
            'measured_kw': ['mean', 'count']
        }).reset_index()
        
        print(agg_df.shape)
        
        # Flatten column names
        agg_df.columns = ['asset_id', 'asset_type', 'delivery_start', 'measured_kw', 'measurement_count']
        
        print(agg_df['measured_kw'].head())
        print(agg_df['measurement_count'].head())
        
        # Filter for data quality (keeping measurements for any date)
        agg_df = agg_df[
            agg_df['measurement_count'] >= 3  # Require at least 3 measurements per interval
        ]
        
        print("Unique dates found:", sorted(agg_df['delivery_start'].dt.date.unique()))
        
        print("After date filter shape:", agg_df.shape)
        
        # Drop the measurement count column
        agg_df = agg_df.drop('measurement_count', axis=1)
        
        # Handle potential NaN values
        agg_df['measured_kw'] = agg_df['measured_kw'].fillna(0)
    
    # total_measurements = len(all_data)
    # intervals_with_data = len(agg_df) if not df.empty else 0
    # print(f"Processed {total_measurements} measurements into {intervals_with_data} 15-minute intervals")
    return agg_df

def load_forecast_data():
    #Load forecast data for comparison
    try:
        df_forecast = pd.read_csv("../Task1/output/asset_forecasts.csv")
        df_forecast['delivery_start'] = pd.to_datetime(df_forecast['delivery_start']).dt.tz_localize(None)
        print(f"Loaded {len(df_forecast)} forecast records")
        return df_forecast
    except FileNotFoundError:
        print("Forecast data not found")
        return pd.DataFrame()

def compute_best_of_infeed_asset_level(df_measured, df_forecast):
    #Compute best-of-infeed for each asset
    if df_forecast.empty:
        # If no forecast data, use measured data only with quality checks
        best_of_infeed = df_measured.copy()
        best_of_infeed['forecast_kw'] = 0
        best_of_infeed['best_of_infeed_kw'] = best_of_infeed['measured_kw']
        best_of_infeed['data_source'] = 'measured'
    else:
        # Prepare forecast data with proper timezone handling
        df_forecast = df_forecast.rename(columns={'value_kw': 'forecast_kw'})
        df_forecast['delivery_start'] = pd.to_datetime(df_forecast['delivery_start']).dt.tz_localize('Europe/Berlin')
        
        # Adjust measured data date to match forecast date
        # First convert to datetime without timezone
        target_date = pd.to_datetime(df_forecast['delivery_start'].iloc[0]).tz_localize(None).date()
        measured_date = df_measured['delivery_start'].iloc[0].tz_localize(None).date()
        days_diff = (target_date - measured_date).days
        
        print("[DEBUG] Adjusting measured date by", days_diff, "days")
        df_measured['delivery_start'] = df_measured['delivery_start'] + pd.Timedelta(days=days_diff)
        
        # Extract asset type from asset_id for forecasts
        df_forecast['asset_type'] = df_forecast['asset_id'].apply(
            lambda x: 'WND' if 'WND' in x else 'SOL' if 'SOL' in x else 'UNKNOWN'
        )
        
        # Merge forecast and measured data with asset type information
        # First convert delivery_start to same timezone
        df_measured_tz_naive = df_measured.copy()
        df_measured_tz_naive['delivery_start'] = df_measured_tz_naive['delivery_start'].dt.tz_localize(None).dt.tz_localize('Europe/Berlin')
        
        merged = pd.merge(
            df_forecast[['asset_id', 'asset_type', 'delivery_start', 'forecast_kw']], 
            df_measured_tz_naive[['asset_id', 'delivery_start', 'measured_kw']],
            on=['asset_id', 'delivery_start'],
            how='outer'
        )
        
        # Fill missing values appropriately
        merged['measured_kw'] = merged['measured_kw'].fillna(0)
        merged['forecast_kw'] = merged['forecast_kw'].fillna(0)
        
        # Convert to numeric and apply quality checks
        for col in ['measured_kw', 'forecast_kw']:
            merged[col] = pd.to_numeric(merged[col], errors='coerce')
            # Remove physically impossible values (e.g., negative power)
            merged.loc[merged[col] < 0, col] = 0
        
        # Compute best-of-infeed based on asset type and data quality
        merged['best_of_infeed_kw'] = merged.apply(
            lambda row: max(
                row['forecast_kw'] if row['forecast_kw'] >= 0 else 0,
                row['measured_kw'] if row['measured_kw'] >= 0 else 0
            ),
            axis=1
        )
        
        # Track which value was used for best-of-infeed
        merged['data_source'] = merged.apply(
            lambda row: 'measured' if row['measured_kw'] > row['forecast_kw'] else 'forecast',
            axis=1
        )
        
        best_of_infeed = merged[[
            'asset_id', 'asset_type', 'delivery_start', 
            'forecast_kw', 'measured_kw', 'best_of_infeed_kw', 
            'data_source'
        ]].copy()
    
    # Ensure numeric columns are properly typed
    numeric_cols = ['forecast_kw', 'measured_kw', 'best_of_infeed_kw']
    for col in numeric_cols:
        if col in best_of_infeed.columns:
            best_of_infeed[col] = pd.to_numeric(best_of_infeed[col], errors='coerce').fillna(0)
    return best_of_infeed

def compute_portfolio_best_of_infeed(df_asset_best_of_infeed):
    # Aggregate best-of-infeed to portfolio level

    # First compute type-specific aggregations
    type_agg = df_asset_best_of_infeed.groupby(['delivery_start', 'asset_type']).agg({
        'forecast_kw': 'sum',
        'measured_kw': 'sum',
        'best_of_infeed_kw': 'sum',
        'asset_id': 'count'  # Count of assets contributing to each interval
    }).reset_index()
    
    # Compute portfolio totals
    portfolio_best_of_infeed = df_asset_best_of_infeed.groupby('delivery_start').agg({
        'forecast_kw': 'sum',
        'measured_kw': 'sum',
        'best_of_infeed_kw': 'sum',
        'asset_id': 'nunique'  # Count unique assets
    }).reset_index()
    
    # Rename columns for clarity
    portfolio_best_of_infeed.rename(columns={
        'forecast_kw': 'portfolio_forecast_kw',
        'measured_kw': 'portfolio_measured_kw',
        'best_of_infeed_kw': 'portfolio_best_of_infeed_kw',
        'asset_id': 'assets_contributing'
    }, inplace=True)
    
    # print(len(portfolio_best_of_infeed))
    return portfolio_best_of_infeed

def calculate_best_of_infeed_metrics(df_asset, df_portfolio):
    # Calculate key metrics for best-of-infeed analysis

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
        # Calculate accuracy based on RMSE relative to portfolio average
        rmse = np.sqrt(np.mean((df_portfolio['portfolio_forecast_kw'] - 
                              df_portfolio['portfolio_measured_kw'])**2))
        mean_power = df_portfolio['portfolio_measured_kw'].mean()
        
        if mean_power > 0:
            forecast_accuracy = max(0, (1 - (rmse / mean_power)) * 100)
        else:
            forecast_accuracy = 0  # Default when no valid measurements
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
    # Save best-of-infeed results to CSV files
    
    os.makedirs("output", exist_ok=True)
    
    # Save data
    df_asset.to_csv("output/asset_best_of_infeed.csv", index=False)
    df_portfolio.to_csv("output/portfolio_best_of_infeed.csv", index=False)
    
    # Convert numpy types to Python native types for JSON serialization
    json_metrics = {}
    for key, value in metrics.items():
        if isinstance(value, (np.int64, np.int32)):
            json_metrics[key] = int(value)
        elif isinstance(value, (np.float64, np.float32)):
            json_metrics[key] = float(value)
        else:
            json_metrics[key] = value
    
    # Save metrics
    with open("output/best_of_infeed_metrics.json", 'w') as f:
        json.dump(json_metrics, f, indent=2)
    

def main():
   
    # Data directories - normalized path handling
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    live_measured_dir = os.path.join(base_dir, "DataEngineeringChallenge", "DataEngineeringChallenge", 
                                   "src", "vpp", "live_measured_infeed")
    
    df_measured = load_live_measured_data(live_measured_dir)
    
    df_forecast = load_forecast_data()
    #print(df_forecast)
    df_asset_best_of_infeed = compute_best_of_infeed_asset_level(df_measured, df_forecast)
    
    df_portfolio_best_of_infeed = compute_portfolio_best_of_infeed(df_asset_best_of_infeed)
    
    metrics = calculate_best_of_infeed_metrics(df_asset_best_of_infeed, df_portfolio_best_of_infeed)
    
    save_best_of_infeed_data(df_asset_best_of_infeed, df_portfolio_best_of_infeed, metrics)

if __name__ == "__main__":
    main()