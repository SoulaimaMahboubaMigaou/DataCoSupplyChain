import pandas as pd
from connection import engine

query = """
SELECT
    table_name
FROM information_schema.tables
WHERE table_schema = 'dwh'
ORDER BY table_name;
"""

result = pd.read_sql(query, engine)

print("\n Tables du Data Warehouse :\n")
print(result.to_string(index=False))