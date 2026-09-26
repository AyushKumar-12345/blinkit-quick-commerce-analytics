# Blinkit Quick-Commerce Analytics and Operational Intelligence

## Executive Summary
An end-to-end data analytics and business intelligence project analyzing quick-commerce operations across 5,000 orders and INR 4.97M in Gross Merchandise Value (GMV).

This repository implements an automated Python ETL pipeline, an enterprise SQL analytical warehouse covering unit economics and SLA breach latencies, and an interactive 4-page Power BI executive suite designed to diagnose logistics bottlenecks, dark store efficiency, customer retention, and inventory shrinkage.

---

## Pipeline Overview
1. Raw Relational Data: 8 Inbound Datasets
2. Python Automated ETL (`process_blinkit_data.py`)
   - Text sanitization and anomaly cleaning
   - Temporal standardization
   - Feature engineering for SLA breach, latency, and stockout alerts
3. Relational Analytics Warehouse (`blinkit_queries.sql`)
   - Star Schema modeling: 1 Fact, 7 Dimensions
   - RFM customer segmentation using Window functions and NTILE
   - Pareto 80/20 category revenue breakdown
   - Month-over-month growth and dark store SLA ranking
4. Power BI Executive Dashboard
   - 4-page layout with custom dark theme and dynamic DAX modeling

---

## Tech Stack and Tools
- Python: Pandas, NumPy, PIL
- SQL: Advanced CTEs, Window Functions (DENSE_RANK, LAG, NTILE), Relational Constraints
- Power BI: Star Schema data modeling, relationship cardinality optimization, DAX measures

---

## Key Performance Indicators (KPIs)

| Metric | Measured Value | Operational Insight |
|---|---|---|
| Gross Merchandise Value (GMV) | INR 4.97M | Generated across 5,000 completed orders |
| Average Order Value (AOV) | INR 994.48 | Baseline basket size across active user cohorts |
| On-Time Delivery SLA Rate | 69.40% | Operational bottleneck with 30.6% delayed orders |
| Inventory Shrinkage Rate | 3.8% | Tracked across inbound damaged inventory logs |
| Gross Margin | 27.78% | Product portfolio profitability baseline |
| Campaign ROAS | 1.97x | Customer acquisition efficiency multiplier |

---

## Analytical Insights

### 1. Delivery SLA and Dark Store Latency
- Bottleneck: 30.6% of orders missed the promised quick-commerce delivery window.
- Root Cause: Increased delivery distance and peak hub load. Stores with dispatch radii greater than 4.5 km showed a 2.3x increase in SLA breaches.

### 2. Pareto 80/20 Revenue Distribution
- Core product categories (Dairy, Fresh Produce, and Beverages) account for 74.2% of total platform volume.

### 3. Customer RFM Segmentation
- Grouped customer base using Recency, Frequency, and Monetary scores:
  - Champions / VIP: High purchase frequency and recent transactions.
  - At-Risk: High historical spend with over 45 days of inactivity.
  - Hibernating: One-time buyers requiring re-engagement campaigns.

---

## Dashboard Architecture
- Page 1: Business Overview - High-level GMV tracking, daily order volume, and MoM trends.
- Page 2: Product Analysis - Category margin contribution, Pareto analysis, and stock levels.
- Page 3: Delivery and Feedback - Dark store SLA compliance, delay breakdown, and ratings.
- Page 4: Revenue and Marketing - Channel spend vs. revenue, ROAS, and conversion metrics.

---

## Setup Instructions

1. Clone the repository:
   git clone https://github.com/YOUR_USERNAME/blinkit-quick-commerce-analytics.git
   cd blinkit-quick-commerce-analytics

2. Run the automated data processing pipeline:
   python process_blinkit_data.py

3. Execute analytical queries:
   Run the scripts inside `blinkit_queries.sql` in MySQL, PostgreSQL, or SQL Server.

4. View the dashboard:
   Open `Blinkit Sales Analytics.pbix` in Power BI Desktop.

---

## Author
Ayush Kumar
