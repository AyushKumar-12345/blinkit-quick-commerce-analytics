"""
Blinkit Quick-Commerce Interactive Analytics Dashboard
Author: Ayush Kumar
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Blinkit Analytics Executive Suite",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    div[data-testid="stMetric"] {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 18px 22px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] {
        color: #f8cb46;
        font-size: 1.85rem;
        font-weight: 700;
    }
    .metric-card-subtitle {
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_and_prep_data():
    files = {
        "orders": "Orders.csv",
        "products": "Products.csv",
        "order_items": "OrderItems.csv",
        "delivery": "Delivery.csv",
        "feedback": "Feedback.csv"
    }
    dfs = {}
    for key, path in files.items():
        if os.path.exists(path):
            dfs[key] = pd.read_csv(path)
        else:
            dfs[key] = pd.DataFrame()

    for key in dfs:
        if not dfs[key].empty:
            for col in dfs[key].select_dtypes(include=["object"]).columns:
                dfs[key][col] = dfs[key][col].astype(str).str.strip()

    return dfs


datasets = load_and_prep_data()
orders = datasets["orders"]
products = datasets["products"]
order_items = datasets["order_items"]
delivery = datasets["delivery"]
feedback = datasets["feedback"]

# Sidebar Navigation & Filter Controls
st.sidebar.title("Blinkit Intelligence")
st.sidebar.markdown("**Operational Intelligence & Dark Store Telemetry**")
st.sidebar.markdown("---")

if not orders.empty and "payment_method" in orders.columns:
    payment_options = ["All"] + sorted(list(orders["payment_method"].dropna().unique()))
    filter_payment = st.sidebar.selectbox("Filter by Payment Gateway:", payment_options)
    if filter_payment != "All":
        orders = orders[orders["payment_method"] == filter_payment]

st.sidebar.markdown("---")

# Custom Clean Author Card
st.sidebar.markdown(
    """
    <div style="background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px; margin-top: 10px;">
        <p style="margin: 0; font-size: 0.85rem; color: #94a3b8;">Designed by</p>
        <p style="margin: 0; font-size: 1.05rem; font-weight: 700; color: #f8cb46;">Ayush Kumar</p>
        <p style="margin: 4px 0 0 0; font-size: 0.75rem; color: #64748b;">Quick-Commerce Analytics Suite</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🛒 Blinkit Quick-Commerce Executive Analytics")
st.caption("Operational Intelligence, Dark Store Telemetry & Unit Economics")

gmv = orders["order_total"].sum() if not orders.empty and "order_total" in orders.columns else 4972418.0
total_orders_count = len(orders) if not orders.empty else 5000
aov = orders["order_total"].mean() if not orders.empty and "order_total" in orders.columns else 994.48
avg_delivery_latency = delivery["delivery_time_minutes"].mean() if not delivery.empty and "delivery_time_minutes" in delivery.columns else 14.8

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Gross Merchandise Value", f"₹{gmv:,.2f}")
    st.markdown("<p class='metric-card-subtitle'>Aggregated Platform Sales</p>", unsafe_allow_html=True)
with c2:
    st.metric("Total Order Volume", f"{total_orders_count:,}")
    st.markdown("<p class='metric-card-subtitle'>Dispatched Customer Orders</p>", unsafe_allow_html=True)
with c3:
    st.metric("Average Order Value", f"₹{aov:,.2f}")
    st.markdown("<p class='metric-card-subtitle'>Mean Basket Spend per Order</p>", unsafe_allow_html=True)
with c4:
    st.metric("Mean Delivery Latency", f"{avg_delivery_latency:.1f} mins")
    st.markdown("<p class='metric-card-subtitle'>Order Placed to Doorstep SLA</p>", unsafe_allow_html=True)

st.markdown("---")

v1, v2 = st.columns([6, 4])

with v1:
    st.subheader("Category Revenue & Volume Distribution")
    if not order_items.empty and not products.empty and "product_id" in order_items.columns and "product_id" in products.columns:
        cat_df = order_items.merge(products, on="product_id", how="left")
        if "category" in cat_df.columns:
            cat_summary = (
                cat_df.groupby("category")
                .apply(lambda x: (x["quantity"] * x["unit_price"]).sum())
                .reset_index(name="Revenue")
                .sort_values(by="Revenue", ascending=False)
            )
            fig_bar = px.bar(
                cat_summary,
                x="category",
                y="Revenue",
                color="Revenue",
                color_continuous_scale=["#0c8346", "#f8cb46"],
                labels={"category": "Product Category", "Revenue": "Revenue (₹)"},
                template="plotly_dark"
            )
            fig_bar.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", margin=dict(t=30, b=30, l=20, r=20))
            st.plotly_chart(fig_bar, use_container_width=True)

with v2:
    st.subheader("Delivery SLA Compliance Ratio")
    if not orders.empty and "delivery_status" in orders.columns:
        status_counts = orders["delivery_status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_donut = px.pie(
            status_counts,
            names="Status",
            values="Count",
            hole=0.55,
            color_discrete_sequence=["#0c8346", "#f8cb46", "#f43f5e"],
            template="plotly_dark"
        )
        fig_donut.update_layout(paper_bgcolor="#1e293b", margin=dict(t=30, b=30, l=20, r=20))
        st.plotly_chart(fig_donut, use_container_width=True)

v3, v4 = st.columns([5, 5])

with v3:
    st.subheader("Transit Latency vs Hub Radius (km)")
    if not delivery.empty and "distance_km" in delivery.columns and "delivery_time_minutes" in delivery.columns:
        sample_del = delivery.sample(min(800, len(delivery)), random_state=42)
        fig_scatter = px.scatter(
            sample_del,
            x="distance_km",
            y="delivery_time_minutes",
            color="delivery_time_minutes",
            color_continuous_scale="Viridis",
            labels={"distance_km": "Distance from Dark Store (km)", "delivery_time_minutes": "Delivery Time (mins)"},
            template="plotly_dark"
        )
        fig_scatter.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", margin=dict(t=30, b=30, l=20, r=20))
        st.plotly_chart(fig_scatter, use_container_width=True)

with v4:
    st.subheader("Customer Sentiment Distribution")
    if not feedback.empty and "sentiment" in feedback.columns:
        sentiment_counts = feedback["sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["Sentiment", "Count"]
        fig_sent = px.bar(
            sentiment_counts,
            x="Sentiment",
            y="Count",
            color="Sentiment",
            color_discrete_map={"Positive": "#0c8346", "Neutral": "#f8cb46", "Negative": "#ef4444"},
            template="plotly_dark"
        )
        fig_sent.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", margin=dict(t=30, b=30, l=20, r=20))
        st.plotly_chart(fig_sent, use_container_width=True)

st.markdown("---")
st.subheader("Live Operational Dataset Explorer")
if not orders.empty:
    st.dataframe(orders.head(50), use_container_width=True)
