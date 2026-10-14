from sqlalchemy import text
from connection import engine


try:

    with engine.begin() as connection:

        connection.execute(
            text("CREATE SCHEMA IF NOT EXISTS staging")
        )

    print("✅ Schema 'staging' créé avec succès !")


except Exception as e:

    print("❌ Erreur :")
    print(e)