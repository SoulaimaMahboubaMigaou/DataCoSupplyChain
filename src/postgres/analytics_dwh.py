import pandas as pd
from connection import engine


def run_query(title, query):

    print(f"\n{'=' * 60}")
    print(f"📊 {title}")
    print('=' * 60)

    result = pd.read_sql(query, engine)

    print(result.to_string(index=False))

    return result


# ============================================================
# 1. KPI GÉNÉRAUX
# ============================================================

query_kpi = """
SELECT
    COUNT(*) AS total_order_items,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(sales)::numeric, 2) AS total_sales,
    ROUND(AVG(sales)::numeric, 2) AS avg_sales,
    ROUND(AVG(delivery_delay)::numeric, 2) AS avg_delivery_delay,
    ROUND(
        100.0 * AVG(late_delivery_risk),
        2
    ) AS late_delivery_rate
FROM dwh.fact_orders;
"""

run_query("KPI GÉNÉRAUX", query_kpi)


# ============================================================
# 2. PERFORMANCE PAR MODE DE LIVRAISON
# ============================================================

query_shipping = """
SELECT
    s.shipping_mode,
    COUNT(*) AS order_items,
    ROUND(SUM(f.sales)::numeric, 2) AS total_sales,
    ROUND(AVG(f.delivery_delay)::numeric, 2) AS avg_delay,
    ROUND(
        100.0 * AVG(f.late_delivery_risk),
        2
    ) AS late_rate
FROM dwh.fact_orders f
JOIN dwh.dim_shipping s
    ON f.shipping_key = s.shipping_key
GROUP BY s.shipping_mode
ORDER BY late_rate DESC;
"""

run_query("PERFORMANCE PAR MODE DE LIVRAISON", query_shipping)


# ============================================================
# 3. PERFORMANCE PAR RÉGION
# ============================================================

query_region = """
SELECT
    l.region,
    COUNT(*) AS order_items,
    ROUND(SUM(f.sales)::numeric, 2) AS total_sales,
    ROUND(AVG(f.delivery_delay)::numeric, 2) AS avg_delay,
    ROUND(
        100.0 * AVG(f.late_delivery_risk),
        2
    ) AS late_rate
FROM dwh.fact_orders f
JOIN dwh.dim_location l
    ON f.location_key = l.location_key
GROUP BY l.region
ORDER BY late_rate DESC;
"""

run_query("PERFORMANCE PAR RÉGION", query_region)


# ============================================================
# 4. PERFORMANCE PAR PAYS
# ============================================================

query_country = """
SELECT
    l.country,
    COUNT(*) AS order_items,
    ROUND(SUM(f.sales)::numeric, 2) AS total_sales,
    ROUND(
        100.0 * AVG(f.late_delivery_risk),
        2
    ) AS late_rate
FROM dwh.fact_orders f
JOIN dwh.dim_location l
    ON f.location_key = l.location_key
GROUP BY l.country
ORDER BY late_rate DESC
LIMIT 15;
"""

run_query("TOP 15 PAYS À RISQUE", query_country)


# ============================================================
# 5. PERFORMANCE MENSUELLE
# ============================================================

query_monthly = """
SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(*) AS order_items,
    ROUND(SUM(f.sales)::numeric, 2) AS total_sales,
    ROUND(
        100.0 * AVG(f.late_delivery_risk),
        2
    ) AS late_rate
FROM dwh.fact_orders f
JOIN dwh.dim_date d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.month;
"""

run_query("ÉVOLUTION MENSUELLE", query_monthly)


# ============================================================
# 6. PERFORMANCE PAR CATÉGORIE PRODUIT
# ============================================================

query_category = """
SELECT
    p.category_name,
    COUNT(*) AS order_items,
    ROUND(SUM(f.sales)::numeric, 2) AS total_sales,
    ROUND(
        100.0 * AVG(f.late_delivery_risk),
        2
    ) AS late_rate
FROM dwh.fact_orders f
JOIN dwh.dim_product p
    ON f.product_key = p.product_key
GROUP BY p.category_name
ORDER BY total_sales DESC;
"""

run_query("PERFORMANCE PAR CATÉGORIE", query_category)


# ============================================================
# 7. TOP PRODUITS
# ============================================================

query_products = """
SELECT
    p.product_name,
    COUNT(*) AS order_items,
    ROUND(SUM(f.sales)::numeric, 2) AS total_sales,
    ROUND(
        SUM(f.benefit_per_order)::numeric,
        2
    ) AS total_benefit
FROM dwh.fact_orders f
JOIN dwh.dim_product p
    ON f.product_key = p.product_key
GROUP BY p.product_name
ORDER BY total_sales DESC
LIMIT 10;
"""

run_query("TOP 10 PRODUITS", query_products)


# ============================================================
# 8. CLIENTS À FORTE VALEUR
# ============================================================

query_customers = """
SELECT
    c.customer_key,
    c.customer_id,
    c.segment,
    c.country,
    COUNT(*) AS order_items,
    ROUND(SUM(f.sales)::numeric, 2) AS total_sales
FROM dwh.fact_orders f
JOIN dwh.dim_customer c
    ON f.customer_key = c.customer_key
GROUP BY
    c.customer_key,
    c.customer_id,
    c.segment,
    c.country
ORDER BY total_sales DESC
LIMIT 10;
"""

run_query("TOP 10 CLIENTS", query_customers)


print("\n Analyse SQL du Data Warehouse terminée !")