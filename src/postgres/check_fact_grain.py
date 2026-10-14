import pandas as pd
from connection import engine


query = """
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT order_item_id) AS unique_order_items,
    COUNT(*) - COUNT(DISTINCT order_item_id) AS duplicates
FROM staging.orders;
"""

result = pd.read_sql(query, engine)

print("\n📦 Vérification du grain :\n")
print(result.to_string(index=False))