from sqlalchemy import text
from connection import engine


try:

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT current_database();")
        )

        database = result.fetchone()[0]

        print("✅ Connexion réussie !")
        print("📊 Database :", database)


except Exception as e:

    print("❌ Erreur de connexion :")
    print(e)