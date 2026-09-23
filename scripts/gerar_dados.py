import os
import psycopg2
from dotenv import load_dotenv
from faker import Faker
import random

load_dotenv()
fake = Faker("pt_BR")

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()




##########################################################################
cur.execute("SELECT id FROM pedidos;")
ids_pedidos = [linha[0] for linha in cur.fetchall()]

cur.execute("SELECT id, preco_produto FROM produtos;")
produtos = cur.fetchall()  # cada item aqui vem como uma tupla: (id, preco)

NUM_ITENS = 750

for _ in range(NUM_ITENS):
    pedido_id = random.choice(ids_pedidos)
    produto_id, preco_unitario = random.choice(produtos)
    quantidade = random.randint(1, 10)

    cur.execute(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (%s, %s, %s, %s);",
        (pedido_id, produto_id, quantidade, preco_unitario)
    )

conn.commit()
print(f"{NUM_ITENS} itens de pedido inseridos com sucesso.")