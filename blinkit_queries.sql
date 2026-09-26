-- =====================================================================
-- BLINKIT QUICK-COMMERCE ENTERPRISE ANALYTICS & KPI SUITE
-- Target Engines: MySQL 8.0+ / PostgreSQL / Snowflake / MS SQL Server
-- Description: Advanced analytical queries covering unit economics, 
--              delivery SLA latency, customer RFM, and dark store inventory.
-- =====================================================================

CREATE DATABASE IF NOT EXISTS blinkit_analytics;
USE blinkit_analytics;

-- =====================================================================
-- 1. SCHEMA DEFINITION & CONSTRAINTS
-- =====================================================================

CREATE TABLE IF NOT EXISTS products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    brand VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    mrp DECIMAL(10,2) NOT NULL,
    margin_percentage DECIMAL(5,2),
    shelf_life_days INT,
    min_stock_level INT,
    max_stock_level INT
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(20),
    address VARCHAR(255),
    area VARCHAR(100),
    pincode VARCHAR(20),
    registration_date DATE NOT NULL,
    customer_segment VARCHAR(50),
    total_orders INT DEFAULT 0,
    avg_order_value DECIMAL(10,2) DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS orders (
    order_id BIGINT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATETIME NOT NULL,
    promised_delivery_time DATETIME,
    actual_delivery_time DATETIME,
    delivery_status VARCHAR(50),
    order_total DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    delivery_partner_id INT,
    store_id INT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id BIGINT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS delivery_performance (
    order_id BIGINT PRIMARY KEY,
    delivery_partner_id INT NOT NULL,
    promised_time DATETIME,
    actual_time DATETIME,
    delivery_time_minutes INT,
    distance_km DECIMAL(5,2),
    delivery_status VARCHAR(50),
    reasons_if_delayed VARCHAR(255),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE IF NOT EXISTS customer_feedback (
    feedback_id INT PRIMARY KEY,
    order_id BIGINT,
    customer_id INT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    feedback_category VARCHAR(100),
    sentiment VARCHAR(50),
    feedback_date DATE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS marketing_performance (
    campaign_id INT,
    campaign_name VARCHAR(100),
    date DATE,
    target_audience VARCHAR(100),
    channel VARCHAR(50),
    impressions INT,
    clicks INT,
    conversions INT,
    spend DECIMAL(10,2),
    revenue_generated DECIMAL(10,2),
    roas DECIMAL(5,2)
);

CREATE TABLE IF NOT EXISTS inventory (
    product_id INT,
    date DATE,
    stock_received INT,
    damaged_stock INT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);


-- =====================================================================
-- 2. CORE EXECUTIVE DASHBOARD KPIs
-- =====================================================================

-- High-Level Executive Scorecard
SELECT 
    COUNT(DISTINCT o.order_id) AS total_orders_fulfilled,
    COUNT(DISTINCT o.customer_id) AS total_active_customers,
    CONCAT('₹', FORMAT(ROUND(SUM(o.order_total), 2), 2)) AS gross_merchandise_value,
    CONCAT('₹', FORMAT(ROUND(AVG(o.order_total), 2), 2)) AS blended_aov,
    ROUND(AVG(dp.delivery_time_minutes), 1) AS avg_fulfillment_latency_mins,
    CONCAT(ROUND(SUM(CASE WHEN dp.delivery_time_minutes <= 15 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2), '%') AS under_15min_sla_rate
FROM orders o
LEFT JOIN delivery_performance dp ON o.order_id = dp.order_id;


-- =====================================================================
-- 3. ADVANCED ANALYTICAL ENGINE (CTEs, WINDOW FUNCTIONS & SEGMENTATION)
-- =====================================================================

-- I. Category Pareto Analysis (80/20 Rule: Cumulative Revenue Contribution)
WITH CategoryContribution AS (
    SELECT 
        p.category,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS category_revenue,
        SUM(oi.quantity) AS total_units_sold
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category
),
RankedCategories AS (
    SELECT 
        category,
        category_revenue,
        total_units_sold,
        SUM(category_revenue) OVER () AS total_platform_revenue,
        SUM(category_revenue) OVER (ORDER BY category_revenue DESC) AS running_cumulative_revenue
    FROM CategoryContribution
)
SELECT 
    category,
    category_revenue,
    total_units_sold,
    ROUND((category_revenue / total_platform_revenue) * 100, 2) AS revenue_pct_share,
    ROUND((running_cumulative_revenue / total_platform_revenue) * 100, 2) AS pareto_cumulative_pct
FROM RankedCategories
ORDER BY category_revenue DESC;


-- II. RFM Customer Behavioral Segmentation (Recency, Frequency, Monetary)
WITH CustomerRFM_Raw AS (
    SELECT 
        customer_id,
        DATEDIFF((SELECT MAX(order_date) FROM orders), MAX(order_date)) AS recency_days,
        COUNT(DISTINCT order_id) AS frequency,
        ROUND(SUM(order_total), 2) AS monetary_value
    FROM orders
    GROUP BY customer_id
),
RFM_Scores AS (
    SELECT 
        customer_id,
        recency_days,
        frequency,
        monetary_value,
        NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary_value ASC) AS m_score
    FROM CustomerRFM_Raw
)
SELECT 
    customer_id,
    recency_days,
    frequency,
    monetary_value,
    (r_score + f_score + m_score) AS composite_rfm_score,
    CASE 
        WHEN (r_score + f_score + m_score) >= 10 THEN 'Champions / VIP'
        WHEN (r_score + f_score + m_score) BETWEEN 7 AND 9 THEN 'Loyal High-Value'
        WHEN (r_score + f_score + m_score) BETWEEN 4 AND 6 THEN 'At Risk / Potential Churn'
        ELSE 'Hibernating / Inactive'
    END AS customer_lifecycle_tier
FROM RFM_Scores
ORDER BY composite_rfm_score DESC;


-- III. Dark Store Delivery SLA & Latency Breakdown
WITH StoreFulfillment AS (
    SELECT 
        o.store_id,
        COUNT(o.order_id) AS total_dispatches,
        AVG(dp.delivery_time_minutes) AS avg_transit_time,
        SUM(CASE WHEN dp.delivery_time_minutes > 15 THEN 1 ELSE 0 END) AS delayed_orders,
        AVG(dp.distance_km) AS avg_hub_radius_km
    FROM orders o
    JOIN delivery_performance dp ON o.order_id = dp.order_id
    GROUP BY o.store_id
)
SELECT 
    store_id,
    total_dispatches,
    ROUND(avg_transit_time, 2) AS avg_transit_minutes,
    delayed_orders,
    ROUND((delayed_orders * 100.0 / total_dispatches), 2) AS sla_breach_rate_pct,
    ROUND(avg_hub_radius_km, 2) AS avg_radius_km,
    DENSE_RANK() OVER (ORDER BY (delayed_orders * 100.0 / total_dispatches) ASC) AS dark_store_efficiency_rank
FROM StoreFulfillment
ORDER BY sla_breach_rate_pct ASC;


-- IV. Month-over-Month (MoM) GMV & Order Growth Trajectory
WITH MonthlySales AS (
    SELECT 
        DATE_FORMAT(order_date, '%Y-%m') AS sales_month,
        COUNT(order_id) AS total_orders,
        ROUND(SUM(order_total), 2) AS gmv
    FROM orders
    GROUP BY DATE_FORMAT(order_date, '%Y-%m')
)
SELECT 
    sales_month,
    total_orders,
    gmv,
    LAG(gmv, 1) OVER (ORDER BY sales_month) AS prior_month_gmv,
    ROUND(((gmv - LAG(gmv, 1) OVER (ORDER BY sales_month)) / LAG(gmv, 1) OVER (ORDER BY sales_month)) * 100, 2) AS mom_gmv_growth_pct
FROM MonthlySales
ORDER BY sales_month;


-- V. Inventory Shrinkage & Damage Vulnerability Matrix
SELECT 
    p.category,
    p.product_name,
    SUM(inv.stock_received) AS aggregate_inbound_stock,
    SUM(inv.damaged_stock) AS aggregate_damaged_units,
    ROUND((SUM(inv.damaged_stock) * 100.0 / NULLIF(SUM(inv.stock_received), 0)), 2) AS shrinkage_damage_rate_pct,
    DENSE_RANK() OVER (
        PARTITION BY p.category 
        ORDER BY (SUM(inv.damaged_stock) * 100.0 / NULLIF(SUM(inv.stock_received), 0)) DESC
    ) AS category_vulnerability_rank
FROM inventory inv
JOIN products p ON inv.product_id = p.product_id
GROUP BY p.category, p.product_name
HAVING aggregate_inbound_stock > 0
ORDER BY shrinkage_damage_rate_pct DESC;


-- VI. Marketing Channel Efficiency (CAC vs. ROAS Analysis)
SELECT 
    channel,
    SUM(impressions) AS total_impressions,
    SUM(clicks) AS total_traffic_clicks,
    SUM(conversions) AS net_acquisitions,
    ROUND(SUM(spend), 2) AS gross_ad_spend,
    ROUND(SUM(revenue_generated), 2) AS attribution_revenue,
    ROUND(SUM(spend) / NULLIF(SUM(conversions), 0), 2) AS customer_acquisition_cost,
    ROUND(SUM(revenue_generated) / NULLIF(SUM(spend), 0), 2) AS realized_roas
FROM marketing_performance
GROUP BY channel
ORDER BY realized_roas DESC;
