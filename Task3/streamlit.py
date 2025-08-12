# FlexPower Task 3: Simple Streamlit Dashboard

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path
from Trading import load_trading_data, calculate_trading_metrics

# Page config
st.set_page_config(page_title="FlexPower Trading Metrics", page_icon="⚡", layout="wide")

@st.cache_data
def load_data():
    # Load trading data
    # Try to load saved data first
    if Path("output/trading_data.csv").exists():
        df_trades = pd.read_csv("output/trading_data.csv")
        asset_metrics = pd.read_csv("output/asset_trading_metrics.csv")
        with open("output/portfolio_trading_metrics.json", 'r') as f:
            portfolio_metrics = json.load(f)
    else:
        # Load fresh data from CSV
        df_private, df_public = load_trading_data()
        df_trades, asset_metrics, portfolio_metrics = calculate_trading_metrics(df_private)
    
    return df_trades, asset_metrics, portfolio_metrics

def create_revenue_chart(df_trades):
    # Simple revenue chart
    buy_revenue = df_trades[df_trades['side'] == 'buy']['revenue_eur'].sum()
    sell_revenue = df_trades[df_trades['side'] == 'sell']['revenue_eur'].sum()
    net_revenue = buy_revenue + sell_revenue
    
    fig = go.Figure(data=[
        go.Bar(x=['Buy Revenue', 'Sell Revenue', 'Net Revenue'], 
               y=[buy_revenue, sell_revenue, net_revenue],
               marker_color=['#ff6b6b', '#51cf66', '#339af0'],
               text=[f"€{v:,.0f}" for v in [buy_revenue, sell_revenue, net_revenue]],
               textposition='outside')
    ])
    fig.update_layout(title="Trading Revenue Breakdown", height=400, showlegend=False)
    return fig

def create_volume_chart(df_trades):
    # Simple volume chart
    buy_volume = df_trades[df_trades['side'] == 'buy']['volume_mw'].sum()
    sell_volume = df_trades[df_trades['side'] == 'sell']['volume_mw'].sum()
    
    fig = go.Figure(data=[
        go.Bar(x=['Buy Volume', 'Sell Volume'], 
               y=[buy_volume, sell_volume],
               marker_color=['#ffd43b', '#74c0fc'],
               text=[f"{v:.1f} MW" for v in [buy_volume, sell_volume]],
               textposition='outside')
    ])
    fig.update_layout(title="Trading Volume (MW)", height=400, showlegend=False)
    return fig

def create_trades_timeline(df_trades):
    # Simple timeline chart
    df_trades['DeliveryStart'] = pd.to_datetime(df_trades['DeliveryStart'])
    df_trades['hour'] = df_trades['DeliveryStart'].dt.hour
    
    # Count trades by hour and side
    hourly_data = df_trades.groupby(['hour', 'side']).size().unstack(fill_value=0)
    
    fig = go.Figure()
    
    if 'buy' in hourly_data.columns:
        fig.add_trace(go.Scatter(x=hourly_data.index, y=hourly_data['buy'], 
                                mode='lines+markers', name='Buy Trades', 
                                line=dict(color='#ff6b6b', width=3)))
    
    if 'sell' in hourly_data.columns:
        fig.add_trace(go.Scatter(x=hourly_data.index, y=hourly_data['sell'], 
                                mode='lines+markers', name='Sell Trades',
                                line=dict(color='#51cf66', width=3)))
    
    fig.update_layout(title="Trades by Hour of Day", 
                     xaxis_title="Hour", 
                     yaxis_title="Number of Trades", 
                     height=400)
    return fig

def create_price_distribution(df_trades):
    # Price distribution histogram
    fig = go.Figure(data=[
        go.Histogram(x=df_trades['price_eur_mwh'], nbinsx=20, 
                    marker_color='#845ec2', opacity=0.7)
    ])
    fig.update_layout(title="Price Distribution", 
                     xaxis_title="Price (EUR/MWh)", 
                     yaxis_title="Number of Trades", 
                     height=400)
    return fig

def main():
    st.title("⚡ FlexPower Task3: Trading Metrics Dashboard")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading trading data..."):
        df_trades, asset_metrics, portfolio_metrics = load_data()
    
    st.success(f"✅ Loaded {len(df_trades)} trades successfully!")
    
    # Key metrics
    st.markdown("## 📊 Key Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        revenue = portfolio_metrics['total_revenue_eur']
        st.metric("Total Revenue", f"€{revenue:,.0f}", 
                 delta=f"€{revenue/1000:.1f}k")
    
    with col2:
        total_trades = portfolio_metrics['total_trades']
        st.metric("Total Trades", f"{total_trades}", 
                 delta=f"{portfolio_metrics['buy_trades']} buy / {portfolio_metrics['sell_trades']} sell")
    
    with col3:
        net_vol = portfolio_metrics['net_traded_volume_mw']
        st.metric("Net Volume", f"{net_vol:+.2f} MW", 
                 delta="Long" if net_vol > 0 else "Short" if net_vol < 0 else "Balanced")
    
    with col4:
        vwap = portfolio_metrics['portfolio_vwap']
        st.metric("Portfolio VWAP", f"€{vwap:.2f}/MWh")
    
    st.markdown("---")
    
    # Charts
    st.markdown("## 📈 Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_revenue_chart(df_trades), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_volume_chart(df_trades), use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_trades_timeline(df_trades), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_price_distribution(df_trades), use_container_width=True)
    
    # Asset performance table
    st.markdown("## 🏭 Asset Performance")
    
    # Format asset metrics for display
    display_metrics = asset_metrics.copy()
    display_metrics['revenue_eur'] = display_metrics['revenue_eur'].apply(lambda x: f"€{x:,.2f}")
    display_metrics['total_volume_mw'] = display_metrics['total_volume_mw'].apply(lambda x: f"{x:.2f} MW")
    display_metrics['net_volume_mw'] = display_metrics['net_volume_mw'].apply(lambda x: f"{x:+.2f} MW")
    display_metrics['vwap_eur_mwh'] = display_metrics['vwap_eur_mwh'].apply(lambda x: f"€{x:.2f}/MWh")
    
    st.dataframe(display_metrics.sort_values('revenue_eur', ascending=False), use_container_width=True)
    
    # Trade details
    st.markdown("## 📋 Trading Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Trading Breakdown:**")
        st.write(f"- Buy trades: {portfolio_metrics['buy_trades']}")
        st.write(f"- Sell trades: {portfolio_metrics['sell_trades']}")
        st.write(f"- Total volume: {portfolio_metrics['total_volume_mw']:.2f} MW")
        
    with col2:
        st.write("**Performance Highlights:**")
        best_asset = asset_metrics.loc[asset_metrics['revenue_eur'].idxmax(), 'asset_id']
        most_active = asset_metrics.loc[asset_metrics['num_trades'].idxmax(), 'asset_id']
        st.write(f"- Best performing asset: {best_asset}")
        st.write(f"- Most active asset: {most_active}")
        
        if portfolio_metrics['net_traded_volume_mw'] > 0:
            st.success("📈 Net long position (more selling)")
        elif portfolio_metrics['net_traded_volume_mw'] < 0:
            st.info("📉 Net short position (more buying)")
        else:
            st.info("⚖️ Balanced position")
    
    # Raw data section
    with st.expander("🔍 View Raw Trading Data"):
        st.markdown("**Sample of trading data:**")
        display_cols = ['TradeId', 'Side', 'DeliveryStart', 'Volume', 'Price', 'revenue_eur']
        available_cols = [col for col in display_cols if col in df_trades.columns]
        st.dataframe(df_trades[available_cols].head(20))
        
        st.markdown(f"**Total records:** {len(df_trades)}")

if __name__ == "__main__":
    main()