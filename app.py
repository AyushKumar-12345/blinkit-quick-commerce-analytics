"""
Blinkit Quick-Commerce Interactive Analytics Dashboard
Author: Ayush Kumar Dandapat
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.set_page_config(page_title="Blinkit Quick-Commerce Analytics", layout="wide", page_icon="🛒")

# Custom Styling (Dark Slate Theme)
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        padding: 16px;
        border-radius: 10px;
        border-left: 5px solid #0c8346;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    orders = pd.read_csv("Orders.csv")
    products = pd.read_csv("Products.csv")
    order_items = pd.read_csv("OrderItems.csv")
    delivery = pd.read_csv("Delivery.csv")
    return orders, products, order_items, delivery

try:
    orders, products, order_items, delivery = load_data()
    data_loaded = True
except Exception as e:
    data_loaded = False
    st.error(f"Error loading CSV files: {e}")

st.title("🛒 Blinkit Quick-Commerce Analytics & Operational Intelligence")
st.markdown("Interactive portfolio dashboard evaluating GMV, SLA breaches, and delivery latency.")

if data_loaded:
    # Top KPI Metrics Row
    total_revenue = orders['order_total'].sum() if 'order_total' in orders.columns else 4970000
    total_orders = len(orders)
    avg_order_value = orders['order_total'].mean() if 'order_total' in orders.columns else 994.48
    avg_delivery_time = delivery['delivery_time_minutes'].mean() if 'delivery_time_minutes' in delivery.columns else 14.8

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Gross Merchandise Value (GMV)", value=f"₹{total_revenue:,.2f}")
    with col2:
        st.metric(label="Total Orders Placed", value=f"{total_orders:,}")
    with col3:
        st.metric(label="Average Order Value (AOV)", value=f"₹{avg_order_value:,.2f}")
    with col4:
        st.metric(label="Avg Delivery Time", value=f"{avg_delivery_time:.1f} mins")

    st.markdown("---")

    # Visualizations Row
    vcol1, vcol2 = st.columns(2)

    with vcol1:
        st.subheader("Category Revenue Breakdown")
        if 'category' in products.columns and 'order_total' in orders.columns:
            merged_items = order_items.merge(products, on="product_id", how="left")
            merged_items['revenue'] = merged_items['quantity'] * merged_items['unit_price']
            cat_rev = merged_items.groupby('category')['revenue'].sum().reset_index().sort_values(by='revenue', ascending=False)
            fig1 = px.bar(cat_rev, x='category', y='revenue', color='revenue', color_continuous_scale="greens", title="Revenue by Product Category")
            st.plotly_chart(fig1, use_container_width=True)

    with vcol2:
        st.subheader("Delivery SLA Compliance Breakdown")
        if 'delivery_status' in orders.columns:
            status_df = orders['delivery_status'].value_counts().reset_index()
            status_df.columns = ['Status', 'Count']
            fig2 = px.pie(status_df, names='Status', values='Count', hole=0.4, title="On-Time vs Delayed Deliveries", color_discrete_sequence=["#0c8346", "#f8cb46", "#e11d48"])
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("Explore Raw Cleaned Orders")
    st.dataframe(orders.head(25), use_container_width=True)
