import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from simple_invoice_generator import generate_all_invoices, save_invoices

# Set page config
st.set_page_config(
    page_title="FlexPower Invoice Dashboard",
    page_icon="💰",
    layout="wide"
)

# Title
st.title("💰 FlexPower Task5: Invoice Dashboard")
st.markdown("---")

# Generate new invoices button
if st.button("🔄 Generate New Invoices"):
    with st.spinner("Generating invoices..."):
        invoices = generate_all_invoices()
        save_invoices(invoices)
        st.success(f"Generated {len(invoices)} invoices!")

# Load and display invoices
try:
    with open("output/invoices.json", "r") as f:
        invoices = json.load(f)
    df = pd.DataFrame(invoices)

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Invoices", len(invoices))
    with col2:
        st.metric("Total Gross Amount (EUR)", f"{df['total_gross'].sum():,.2f}")
    with col3:
        st.metric("Average Invoice (EUR)", f"{df['total_gross'].mean():,.2f}")

    # Asset breakdown
    st.subheader("📊 Asset Breakdown")
    
    # Display as table
    st.dataframe(
        df.style.format({
            'production_mwh': '{:.2f}',
            'base_payout': '{:,.2f}',
            'fees': '{:,.2f}',
            'redispatch_payout': '{:,.2f}',
            'total_net': '{:,.2f}',
            'vat': '{:,.2f}',
            'total_gross': '{:,.2f}'
        })
    )

    # Charts
    st.subheader("📈 Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Production vs Revenue
        chart_data = pd.DataFrame({
            'Asset': df['asset_id'],
            'Production (MWh)': df['production_mwh'],
            'Revenue (EUR)': df['total_gross']
        })
        
        st.bar_chart(data=chart_data.set_index('Asset')['Production (MWh)'])
        st.caption("Production by Asset (MWh)")
        
    with col2:
        # Revenue breakdown
        st.bar_chart(data=chart_data.set_index('Asset')['Revenue (EUR)'])
        st.caption("Revenue by Asset (EUR)")

except FileNotFoundError:
    st.warning("No invoices found. Please generate invoices first.")
except Exception as e:
    st.error(f"Error loading invoices: {str(e)}")

# Footer
st.markdown("---")
st.caption("FlexPower Invoice Dashboard • Updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
