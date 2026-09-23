import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

query = """
   SELECT 
    pe.id AS pedido_id,
    pe.data_pedido,
    c.id AS cliente_id,
    c.nome,
    c.sobrenome,
    p.id AS produto_id,
    p.nome_produto,
    ip.quantidade, 
    ip.preco_unitario,
    (ip.quantidade * ip.preco_unitario) AS valor_total_item
FROM itens_pedido ip 
JOIN pedidos pe ON ip.pedido_id = pe.id
JOIN clientes c ON pe.cliente_id = c.id
JOIN produtos p ON ip.produto_id = p.id
ORDER BY pe.data_pedido
"""

df = pd.read_sql(query, conn)

print(df.shape)
print(df.head())

df.to_csv("dados_ecommerce.csv", index=False)

conn.close()