#Le but est de ne plus réécrire la connexion partout
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


USER = "postgres"
PASSWORD = "souleima"
HOST = "localhost"
PORT = 5432
DATABASE = "dataco_supply_chain"


url = URL.create(
    drivername="postgresql+psycopg2",
    username=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    database=DATABASE
)


engine = create_engine(url)