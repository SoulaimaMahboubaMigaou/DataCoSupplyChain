import pandas as pd
from connection import engine


# Nombre de lignes
query_count = """
SELECT COUNT(*) AS total_rows
FROM staging.orders;
"""


# Premières lignes
query_data = """
SELECT *
FROM staging.orders
LIMIT 5;
"""


try:

    total = pd.read_sql(query_count, engine)

    print(" Nombre de lignes dans PostgreSQL :")
    print(total)

    print("\n Premières lignes :")

    data = pd.read_sql(query_data, engine)

    print(data)


except Exception as e:

    print(" Erreur :")
    print(e)