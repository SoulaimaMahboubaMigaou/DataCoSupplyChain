import pandas as pd
from connection import engine


file_path = "data/processed/DataCo_featured.csv"


# =========================
# 1. Lire le fichier CSV
# =========================

try:

    df = pd.read_csv(
        file_path,
        encoding="utf-8-sig"
    )

except UnicodeDecodeError:

    print("⚠️ UTF-8 impossible, tentative avec latin-1...")

    df = pd.read_csv(
        file_path,
        encoding="latin-1"
    )

print(" Dataset chargé avec succès !")
print(" Nombre de lignes :", len(df))
print(" Nombre de colonnes :", len(df.columns))


# =========================
# 2. Envoyer vers PostgreSQL
# =========================

try:

    df.to_sql(
        name="orders",
        con=engine,
        schema="staging",
        if_exists="replace",
        index=False
    )

    print(" Dataset importé dans PostgreSQL !")
    print(" Table : staging.orders")


except Exception as e:

    print(" Erreur pendant l'import :")
    print(e)