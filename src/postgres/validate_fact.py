import pandas as pd
from connection import engine


query = """
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT order_item_key) AS unique_order_items,
    SUM(quantity) AS total_quantity,
    SUM(sales) AS total_sales,
    SUM(benefit_per_order) AS total_benefit,
    AVG(delivery_delay) AS avg_delivery_delay,
    AVG(late_delivery_risk) AS late_risk_rate
FROM dwh.fact_orders;
"""


try:

    result = pd.read_sql(query, engine)

    print("\n Vérification de fact_orders :\n")
    print(result.to_string(index=False))

except Exception as e:

    print(" Erreur :")
    print(e)

# pour Vérifier qu'on n'a pas perdu de lignes

query = """
SELECT

    (
        SELECT COUNT(DISTINCT order_item_id)
        FROM staging.orders
        WHERE order_item_id IS NOT NULL
    ) AS staging_items,

    (
        SELECT COUNT(*)
        FROM dwh.fact_orders
    ) AS fact_items;
"""


result = pd.read_sql(query, engine)

print("\n🔍 Comparaison Staging vs Fact :\n")
print(result.to_string(index=False))