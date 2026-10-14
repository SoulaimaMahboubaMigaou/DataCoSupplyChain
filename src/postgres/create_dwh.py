from sqlalchemy import text
import pandas as pd
from connection import engine


try:

    with engine.begin() as connection:

        connection.execute(
            text("CREATE SCHEMA IF NOT EXISTS dwh")
        )

    print(" Schema 'dwh' créé avec succès !")


except Exception as e:

    print(" Erreur :")
    print(e)



#pour verifier le schema dwh

query = """
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name = 'dwh';
"""

print(pd.read_sql(query, engine))