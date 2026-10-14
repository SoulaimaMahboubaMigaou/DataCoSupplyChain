from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

USER = "postgres"
PASSWORD = "souleima"
HOST = "localhost"
PORT = 5432

# Création de l'URL PostgreSQL 
# #URL.create() permet à SQLAlchemy de gérer correctement les caractères spéciaux dans le mot de passe.
url = URL.create(
    drivername="postgresql+psycopg2",
    username=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    database="postgres"
)

engine = create_engine(url)

try:

    with engine.connect().execution_options(
        isolation_level="AUTOCOMMIT"
    ) as connection:

        print("✅ Connexion PostgreSQL réussie !")

        result = connection.execute(
            text("""
                SELECT 1
                FROM pg_database
                WHERE datname = 'dataco_supply_chain'
            """)
        )

        if result.fetchone() is None:

            connection.execute(
                text("CREATE DATABASE dataco_supply_chain")
            )

            print("✅ Database dataco_supply_chain créée !")

        else:

            print("ℹ️ Database dataco_supply_chain existe déjà !")

except Exception as e:

    print("❌ Erreur :")
    print(e)