import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM clientes;")
resultado = cur.fetchone()
print(f"Clientes cadastrados: {resultado[0]}")

cur.close()
conn.close()