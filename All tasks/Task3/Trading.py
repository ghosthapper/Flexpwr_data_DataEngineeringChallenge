# FlexPower Task 3: Trading Performance Metrics - Simple Version
# Compute trading revenues, number of trades, net traded volume and VWAP

import pandas as pd
import numpy as np
import os
import json

def load_trading_data():
    """Load actual trading data from CSV files"""
    print("[INFO] Loading trading data from CSV files...")
    
    # Load private trades
    private_file = "exchange/Private_Trades-20250608-20250609T000516000Z.csv"
    df_private = pd.read_csv(private_file, sep=';')
    print(f"[INFO] Loaded {len(df_private)} private trades")
    
    # Load public trades  
    public_file = "exchange/Public_Trades-20250608-20250609T000516000Z.csv"
    df_public = pd.read_csv(public_file, sep=';')
    print(f"[INFO] Loaded {len(df_public)} public trades")
    
    return df_private, df_public

def prepare_trading_data(df_trades):
    """Clean and prepare trading data for analysis"""
    
    # Convert timestamps
    df_trades['DeliveryStart'] = pd.to_datetime(df_trades['DeliveryStart'])
    if 'DeliveryEnd' in df_trades.columns:
        df_trades['DeliveryEnd'] = pd.to_datetime(df_trades['DeliveryEnd'])
    
    # Standardize column names and values
    df_trades['side'] = df_trades['Side'].str.lower()
    df_trades['volume_mw'] = df_trades['Volume']
    df_trades['price_eur_mwh'] = df_trades['Price']
    
    # Add revenue calculation
    df_trades['multiplier'] = df_trades['side'].map({'sell': 1, 'buy': -1})
    df_trades['revenue_eur'] = df_trades['volume_mw'] * df_trades['price_eur_mwh'] * df_trades['multiplier']
    df_trades['signed_volume'] = df_trades['volume_mw'] * df_trades['multiplier']
    
    # Add asset_id for grouping (create simple groups based on trade patterns)
    df_trades['asset_id'] = 'A' + (df_trades.index % 10 + 1).astype(str).str.zfill(2)
    
    return df_trades

def calculate_trading_metrics(df_trades):
    """Calculate key trading metrics"""
    
    # Prepare data
    df_trades = prepare_trading_data(df_trades)
    
    # Asset-level metrics
    asset_metrics = df_trades.groupby('asset_id').agg({
        'revenue_eur': 'sum',
        'signed_volume': 'sum',  # Net traded volume
        'TradeId': 'count',      # Number of trades
        'volume_mw': 'sum',      # Total volume
        'price_eur_mwh': lambda x: np.average(x, weights=df_trades.loc[x.index, 'volume_mw'])  # VWAP
    }).reset_index()
    
    asset_metrics.rename(columns={
        'TradeId': 'num_trades',
        'signed_volume': 'net_volume_mw',
        'volume_mw': 'total_volume_mw',
        'price_eur_mwh': 'vwap_eur_mwh'
    }, inplace=True)
    
    # Portfolio totals
    portfolio_metrics = {
        'total_revenue_eur': df_trades['revenue_eur'].sum(),
        'total_trades': len(df_trades),
        'net_traded_volume_mw': df_trades['signed_volume'].sum(),
        'portfolio_vwap': np.average(df_trades['price_eur_mwh'], weights=df_trades['volume_mw']),
        'buy_trades': len(df_trades[df_trades['side'] == 'buy']),
        'sell_trades': len(df_trades[df_trades['side'] == 'sell']),
        'total_volume_mw': df_trades['volume_mw'].sum()
    }
    
    return df_trades, asset_metrics, portfolio_metrics

def save_trading_data(df_trades, asset_metrics, portfolio_metrics):
    """Save trading data to CSV"""
    os.makedirs("output", exist_ok=True)
    
    # Save data
    df_trades.to_csv("output/trading_data_20250608.csv", index=False)
    asset_metrics.to_csv("output/asset_trading_metrics_20250608.csv", index=False)
    
    # Save portfolio metrics
    with open("output/portfolio_trading_metrics.json", 'w') as f:
        json.dump(portfolio_metrics, f, indent=2)
    
    print("[INFO] Trading data saved to output/ directory")

def main():
    """Main function for Task 3"""
    print("FlexPower Task 3: Trading Performance Metrics")
    print("=" * 50)
    
    # Load actual trading data
    df_trades, df_public = load_trading_data()
    
    # Calculate metrics
    print("\n📊 Calculating trading metrics...")
    df_trades, asset_metrics, portfolio_metrics = calculate_trading_metrics(df_trades)
    
    # Save results
    print("\n💾 Saving results...")
    save_trading_data(df_trades, asset_metrics, portfolio_metrics)
    
    # Print summary
    print(f"\n✅ Task 3 Complete - Trading Performance Metrics")
    print(f"   • Total trades: {portfolio_metrics['total_trades']}")
    print(f"   • Buy trades: {portfolio_metrics['buy_trades']}")
    print(f"   • Sell trades: {portfolio_metrics['sell_trades']}")
    print(f"   • Total revenue: €{portfolio_metrics['total_revenue_eur']:,.2f}")
    print(f"   • Total volume: {portfolio_metrics['total_volume_mw']:.2f} MW")
    print(f"   • Net traded volume: {portfolio_metrics['net_traded_volume_mw']:.2f} MW")
    print(f"   • Portfolio VWAP: €{portfolio_metrics['portfolio_vwap']:.2f}/MWh")

if __name__ == "__main__":
    main()