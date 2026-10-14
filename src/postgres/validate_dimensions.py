import pandas as pd
from connection import engine


query = """
SELECT
    table_name,
    (
        SELECT COUNT(*)
        FROM dwh.dim_customer
    ) AS customers,
    (
        SELECT COUNT(*)
        FROM dwh.dim_product
    ) AS products,
    (
        SELECT COUNT(*)
        FROM dwh.dim_shipping
    ) AS shipping,
    (
        SELECT COUNT(*)
        FROM dwh.dim_location
    ) AS locations,
    (
        SELECT COUNT(*)
        FROM dwh.dim_date
    ) AS dates
FROM information_schema.tables
WHERE table_schema = 'dwh'
LIMIT 1;
"""

try:
    result = pd.read_sql(query, engine)

    print("\n📊 Nombre de lignes dans les dimensions :\n")
    print(result.to_string(index=False))

except Exception as e:
    print("❌ Erreur :")
    print(e)