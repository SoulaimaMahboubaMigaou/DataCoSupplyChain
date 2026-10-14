import pandas as pd
from connection import engine


query = """
SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'staging'
  AND table_name = 'orders'
ORDER BY ordinal_position;
"""


try:

    df = pd.read_sql(query, engine)

    print("\n📋 Structure de staging.orders\n")
    print(df.to_string(index=False))

    print("\n✅ Nombre de colonnes :", len(df))

except Exception as e:

    print(" Erreur :")
    print(e)


print("\n🔑 Colonnes contenant probablement des identifiants :")

for column in df["column_name"]:
    if "id" in column.lower():
        print(" -", column)