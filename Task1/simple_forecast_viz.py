import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="FlexPower Task 1 - Forecasting", layout="wide")

def load_data():
    #Load forecast data from CSV files 
    try:
        df_asset = pd.read_csv("output/asset_forecasts.csv")
        df_portfolio = pd.read_csv("output/portfolio_forecast.csv")
        
        # Convert datetime
        df_asset['delivery_start'] = pd.to_datetime(df_asset['delivery_start'])
        df_portfolio['delivery_start'] = pd.to_datetime(df_portfolio['delivery_start'])
        
        return df_asset, df_portfolio, True
        
    except FileNotFoundError:
        return None, None, False

def main():
    st.title("🔋 FlexPower Task 1: Asset & Portfolio Forecasting")
    # st.markdown("**Delivery Day: June 8, 2025**")
    
    # Load data
    df_asset, df_portfolio, data_loaded = load_data()
    
    if not data_loaded:
        st.error("❌ CSV files not found. Please run the main forecasting script first.")
        return
    
    # Sidebar with summary stats
    st.sidebar.header("📊 Summary Stats")
    total_assets = df_asset['asset_id'].nunique()
    portfolio_peak = df_portfolio['portfolio_forecast_kw'].max() / 1000
    portfolio_avg = df_portfolio['portfolio_forecast_kw'].mean() / 1000
    
    st.sidebar.metric("Total Assets", total_assets)
    st.sidebar.metric("Portfolio Peak", f"{portfolio_peak:.1f} MW")
    st.sidebar.metric("Portfolio Average", f"{portfolio_avg:.1f} MW")
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Portfolio Total Forecast")
        
        # Portfolio chart
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        ax1.plot(df_portfolio['delivery_start'], df_portfolio['portfolio_forecast_kw'] / 1000, 
                linewidth=2, color='#1f77b4')
        ax1.set_ylabel('Power (MW)')
        ax1.set_title('Total Portfolio Forecast')
        ax1.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig1)
        
    with col2:
        st.subheader("🏭 Top Assets Forecast")
        
        # Number of assets to show
        # num_assets = st.selectbox("Select number of top assets:", [3, 5, 10], index=1)
        num_assets = 4
        
        # Top assets chart
        top_assets = df_asset.groupby('asset_id')['value_kw'].mean().nlargest(num_assets).index
        
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        for asset in top_assets:
            asset_data = df_asset[df_asset['asset_id'] == asset]
            ax2.plot(asset_data['delivery_start'], asset_data['value_kw'] / 1000, 
                    label=f'Asset {asset}', linewidth=2)
        
        ax2.set_ylabel('Power (MW)')
        ax2.set_title(f'Top {num_assets} Assets Forecast')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig2)
    
    # Data tables
    st.subheader("📋 Forecast Data")
    
    tab1, tab2 = st.tabs(["Portfolio Data", "Asset Data"])
    
    with tab1:
        st.dataframe(df_portfolio.head(20), use_container_width=True)
        
    with tab2:
        st.dataframe(df_asset.head(20), use_container_width=True)

if __name__ == "__main__":
    main()