import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json

st.set_page_config(page_title="FlexPower Task 2 - Best-of-Infeed", layout="wide")

def load_data():
    # Load data safely
    try:
        df_asset = pd.read_csv("output/asset_best_of_infeed.csv")
        df_portfolio = pd.read_csv("output/portfolio_best_of_infeed.csv")
        
        # Convert datetime
        df_asset['delivery_start'] = pd.to_datetime(df_asset['delivery_start'])
        df_portfolio['delivery_start'] = pd.to_datetime(df_portfolio['delivery_start'])
        
        # Convert ALL numeric columns to float
        for col in df_asset.columns:
            if 'kw' in col.lower():
                df_asset[col] = pd.to_numeric(df_asset[col], errors='coerce').fillna(0)
        
        for col in df_portfolio.columns:
            if 'kw' in col.lower():
                df_portfolio[col] = pd.to_numeric(df_portfolio[col], errors='coerce').fillna(0)
        
        with open("output/best_of_infeed_metrics.json", 'r') as f:
            metrics = json.load(f)
            
        return df_asset, df_portfolio, metrics, True
        
    except:
        return None, None, None, False

st.title("⚡ FlexPower Task 2: Best-of-Infeed Analysis")

# Load data
df_asset, df_portfolio, metrics, loaded = load_data()

if not loaded:
    st.error(" Please run task2_best_of_infeed.py first")
    st.stop()

# Sidebar
st.sidebar.metric("Total Assets", int(metrics['total_assets']))
st.sidebar.metric("Portfolio Peak", f"{metrics['portfolio_peak_kw']/1000:.1f} MW")
st.sidebar.metric("Portfolio Average", f"{metrics['portfolio_avg_kw']/1000:.1f} MW")

# Main plots
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Portfolio Best-of-Infeed")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(df_portfolio['delivery_start'], df_portfolio['portfolio_best_of_infeed_kw'] / 1000, 
             linewidth=3, color='red', label='Best-of-Infeed')
    if 'portfolio_forecast_kw' in df_portfolio.columns:
        ax1.plot(df_portfolio['delivery_start'], df_portfolio['portfolio_forecast_kw'] / 1000, 
                linewidth=2, color='blue', alpha=0.7, label='Forecast')
    ax1.set_ylabel('Power (MW)')
    ax1.set_title('Portfolio Analysis')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    st.pyplot(fig1)

with col2:
    st.subheader("🏭 Top Assets")
    # num_assets = st.selectbox("Number of assets:", [3, 5, 8], index=1)
    num_assets = 4
    # Safe way to get top assets - no nlargest!
    asset_means = {}
    for asset in df_asset['asset_id'].unique():
        asset_data = df_asset[df_asset['asset_id'] == asset]
        mean_value = asset_data['best_of_infeed_kw'].mean()
        asset_means[asset] = mean_value
    
    # Sort manually
    sorted_assets = sorted(asset_means.items(), key=lambda x: x[1], reverse=True)
    top_assets = [asset[0] for asset in sorted_assets[:num_assets]]
    
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    for asset in top_assets:
        asset_data = df_asset[df_asset['asset_id'] == asset]
        ax2.plot(asset_data['delivery_start'], asset_data['best_of_infeed_kw'] / 1000, 
                label=f'Asset {asset}', linewidth=2)
    
    ax2.set_ylabel('Power (MW)')
    ax2.set_title(f'Top {num_assets} Assets')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    st.pyplot(fig2)

# Data tables
st.subheader("📋 Data")
tab1, tab2 = st.tabs(["Portfolio", "Assets"])

with tab1:
    st.dataframe(df_portfolio.head(20))

with tab2:
    st.dataframe(df_asset.head(50))