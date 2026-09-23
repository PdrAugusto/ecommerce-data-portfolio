import os
import boto3
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

BUCKET_NAME = "ecommerce-portfolio-pedro"
ARQUIVO_LOCAL = "dados_ecommerce.csv"
CAMINHO_NO_BUCKET = "dados/dados_ecommerce.csv"

s3.upload_file(ARQUIVO_LOCAL, BUCKET_NAME, CAMINHO_NO_BUCKET)

print(f"Arquivo '{ARQUIVO_LOCAL}' enviado para s3://{BUCKET_NAME}/{CAMINHO_NO_BUCKET}")