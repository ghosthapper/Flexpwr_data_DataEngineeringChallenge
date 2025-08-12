# task6_streamlit_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="FlexPower Task 6 - Performance Dashboard",
    page_icon="⚡",
    layout="wide"
)

@st.cache_data
def load_performance_data():
    try:
        df_performance = pd.read_csv("output/performance_data.csv")
        asset_metrics = pd.read_csv("output/asset_metrics.csv")
        
        with open("output/portfolio_metrics.json", "r") as f:
            portfolio_metrics = json.load(f)
        
        with open("output/performance_report.txt", "r") as f:
            report_text = f.read()
        
        return df_performance, asset_metrics, portfolio_metrics, report_text
    
    except FileNotFoundError as e:
        st.error(f"Data files not found: {e}")
        st.error("Please run 'task6_performance_report.py' first to generate the data.")
        return None, None, None, None

def main():
    st.title("⚡ FlexPower Task 6 - Performance Dashboard")
    st.subheader("Portfolio Performance Analysis for 2025-06-08")
    
    # Load data
    df_performance, asset_metrics, portfolio_metrics, report_text = load_performance_data()
    
    if df_performance is None:
        st.stop()
    
    # Use all data without filters
    filtered_df = df_performance
    filtered_metrics = asset_metrics
    
    # Key Metrics Row
    st.header("📊 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_production = filtered_df['actual_mwh'].sum()
        st.metric("Total Production", f"{total_production:.1f} MWh")
    
    with col2:
        total_revenue = filtered_df['net_revenue_eur'].sum()
        st.metric("Net Revenue", f"€{total_revenue:,.0f}")
    
    with col3:
        avg_accuracy = filtered_metrics['forecast_accuracy_pct'].mean() if not filtered_metrics.empty else 0
        st.metric("Avg Forecast Accuracy", f"{avg_accuracy:.1f}%")
    
    with col4:
        avg_capacity_factor = filtered_metrics['capacity_factor_pct'].mean() if not filtered_metrics.empty else 0
        st.metric("Avg Capacity Factor", f"{avg_capacity_factor:.1f}%")
    
    with col5:
        total_imbalance = filtered_df['imbalance_cost_eur'].sum()
        st.metric("Imbalance Costs", f"€{total_imbalance:,.0f}")
    
    # Main Charts
    st.header("📈 Performance Analysis")
    
    # Row 1: Production Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Hourly Production: Forecast vs Actual")
        hourly_data = filtered_df.groupby('hour').agg({
            'forecast_mwh': 'sum',
            'actual_mwh': 'sum'
        }).reset_index()
        
        fig_hourly = go.Figure()
        fig_hourly.add_trace(go.Scatter(
            x=hourly_data['hour'],
            y=hourly_data['actual_mwh'],
            mode='lines+markers',
            name='Actual',
            line=dict(color='blue', width=3)
        ))
        fig_hourly.add_trace(go.Scatter(
            x=hourly_data['hour'],
            y=hourly_data['forecast_mwh'],
            mode='lines+markers',
            name='Forecast',
            line=dict(color='red', width=2, dash='dash')
        ))
        fig_hourly.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Production (MWh)",
            height=400
        )
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with col2:
        st.subheader("Production by Asset")
        asset_production = filtered_df.groupby(['asset_name', 'asset_type'])['actual_mwh'].sum().reset_index()
        
        fig_assets = px.bar(
            asset_production,
            x='asset_name',
            y='actual_mwh',
            color='asset_type',
            color_discrete_map={'Wind': 'lightblue', 'Solar': 'orange'},
            title="Total Production by Asset"
        )
        fig_assets.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_assets, use_container_width=True)
    
    # Row 2: Financial Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Financial Performance by Asset")
        if not filtered_metrics.empty:
            fig_financial = go.Figure()
            fig_financial.add_trace(go.Bar(
                name='Revenue',
                x=filtered_metrics['asset_name'],
                y=filtered_metrics['total_revenue_eur'],
                marker_color='green',
                opacity=0.7
            ))
            fig_financial.add_trace(go.Bar(
                name='Imbalance Cost',
                x=filtered_metrics['asset_name'],
                y=filtered_metrics['imbalance_cost_eur'],
                marker_color='red',
                opacity=0.7
            ))
            fig_financial.update_layout(
                xaxis_title="Asset",
                yaxis_title="Amount (EUR)",
                height=400,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_financial, use_container_width=True)
    
    with col2:
        st.subheader("Asset Performance Metrics")
        if not filtered_metrics.empty:
            fig_performance = go.Figure()
            
            # Capacity factor
            fig_performance.add_trace(go.Bar(
                name='Capacity Factor (%)',
                x=filtered_metrics['asset_name'],
                y=filtered_metrics['capacity_factor_pct'],
                yaxis='y',
                marker_color='lightblue',
                opacity=0.7
            ))
            
            # Forecast accuracy (secondary axis)
            fig_performance.add_trace(go.Scatter(
                name='Forecast Accuracy (%)',
                x=filtered_metrics['asset_name'],
                y=filtered_metrics['forecast_accuracy_pct'],
                yaxis='y2',
                mode='lines+markers',
                line=dict(color='red', width=3),
                marker=dict(size=8)
            ))
            
            fig_performance.update_layout(
                xaxis_title="Asset",
                yaxis=dict(title="Capacity Factor (%)", side="left"),
                yaxis2=dict(title="Forecast Accuracy (%)", side="right", overlaying="y"),
                height=400,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_performance, use_container_width=True)
    
    # Asset Performance Table
    st.header("📋 Asset Performance Summary")
    
    if not filtered_metrics.empty:
        # Format the metrics for display
        display_metrics = filtered_metrics.copy()
        display_metrics['total_revenue_eur'] = display_metrics['total_revenue_eur'].apply(lambda x: f"€{x:,.0f}")
        display_metrics['imbalance_cost_eur'] = display_metrics['imbalance_cost_eur'].apply(lambda x: f"€{x:,.0f}")
        display_metrics['net_revenue_eur'] = display_metrics['net_revenue_eur'].apply(lambda x: f"€{x:,.0f}")
        
        # Rename columns for display
        display_metrics = display_metrics.rename(columns={
            'asset_name': 'Asset Name',
            'asset_type': 'Type',
            'capacity_mw': 'Capacity (MW)',
            'total_actual_mwh': 'Production (MWh)',
            'capacity_factor_pct': 'Capacity Factor (%)',
            'forecast_accuracy_pct': 'Forecast Accuracy (%)',
            'total_revenue_eur': 'Total Revenue',
            'imbalance_cost_eur': 'Imbalance Cost',
            'net_revenue_eur': 'Net Revenue'
        })
        
        st.dataframe(
            display_metrics[[
                'Asset Name', 'Type', 'Capacity (MW)', 'Production (MWh)',
                'Capacity Factor (%)', 'Forecast Accuracy (%)',
                'Total Revenue', 'Net Revenue'
            ]],
            use_container_width=True,
            hide_index=True
        )
    
    # Market Price Analysis
    st.header("💰 Market Price Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Market Price Throughout the Day")
        price_hourly = filtered_df.groupby('hour')['market_price_eur_mwh'].mean().reset_index()
        
        fig_price = px.line(
            price_hourly,
            x='hour',
            y='market_price_eur_mwh',
            title="Average Market Price by Hour"
        )
        fig_price.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Price (EUR/MWh)",
            height=350
        )
        st.plotly_chart(fig_price, use_container_width=True)
    
    with col2:
        st.subheader("Price vs Production Correlation")
        correlation_data = filtered_df.groupby('hour').agg({
            'market_price_eur_mwh': 'mean',
            'actual_mwh': 'sum'
        }).reset_index()
        
        # Fixed: Removed trendline to avoid statsmodels dependency
        fig_correlation = px.scatter(
            correlation_data,
            x='actual_mwh',
            y='market_price_eur_mwh',
            title="Market Price vs Total Production"
        )
        fig_correlation.update_layout(
            xaxis_title="Total Production (MWh)",
            yaxis_title="Market Price (EUR/MWh)",
            height=350
        )
        st.plotly_chart(fig_correlation, use_container_width=True)
    
    # Portfolio Summary
    st.header("🏢 Portfolio Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Key Portfolio Metrics")
        st.write(f"**Total Assets:** {portfolio_metrics['total_assets']}")
        st.write(f"**Total Capacity:** {portfolio_metrics['total_capacity_mw']} MW")
        st.write(f"**Portfolio Capacity Factor:** {portfolio_metrics['portfolio_capacity_factor_pct']}%")
        st.write(f"**Portfolio Forecast Accuracy:** {portfolio_metrics['portfolio_accuracy_pct']}%")
        st.write(f"**Average Market Price:** €{portfolio_metrics['avg_market_price']:.2f}/MWh")
    
    with col2:
        st.subheader("Asset Mix")
        if not filtered_metrics.empty:
            asset_mix = filtered_metrics.groupby('asset_type')['capacity_mw'].sum().reset_index()
            
            fig_mix = px.pie(
                asset_mix,
                values='capacity_mw',
                names='asset_type',
                title="Portfolio Mix by Capacity",
                color_discrete_map={'Wind': 'lightblue', 'Solar': 'orange'}
            )
            fig_mix.update_layout(height=300)
            st.plotly_chart(fig_mix, use_container_width=True)
    
    # Text Report Section
    st.header("📄 Detailed Performance Report")
    
    with st.expander("View Full Text Report", expanded=False):
        st.text(report_text)
    
    # Download Section
    st.header("📥 Data Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Download Performance Data"):
            csv_performance = df_performance.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_performance,
                file_name="performance_data.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Download Asset Metrics"):
            csv_metrics = asset_metrics.to_csv(index=False)
            st.download_button(
                label="Download CSV", 
                data=csv_metrics,
                file_name="asset_metrics.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("Download Text Report"):
            st.download_button(
                label="Download TXT",
                data=report_text,
                file_name="performance_report.txt",
                mime="text/plain"
            )
    
    # Footer
    st.markdown("---")
    st.markdown(f"📊 **FlexPower Task 6 Dashboard** | Data from: 2025-06-08 | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()