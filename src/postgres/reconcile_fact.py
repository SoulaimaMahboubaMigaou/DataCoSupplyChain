# Pour Vérifier les ventes

import pandas as pd
from connection import engine


query = """
SELECT

    (
        SELECT SUM(sales)
        FROM staging.orders
    ) AS staging_sales,

    (
        SELECT SUM(sales)
        FROM dwh.fact_orders
    ) AS fact_sales,

    (
        SELECT SUM(order_item_quantity)
        FROM staging.orders
    ) AS staging_quantity,

    (
        SELECT SUM(quantity)
        FROM dwh.fact_orders
    ) AS fact_quantity;
"""


result = pd.read_sql(query, engine)

print("\n💰 Réconciliation des données :\n")
print(result.to_string(index=False))