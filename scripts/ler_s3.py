import os
import boto3
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

BUCKET_NAME = "ecommerce-portfolio-pedro"
CAMINHO_NO_BUCKET = "dados/dados_ecommerce.csv"

response = s3.get_object(Bucket=BUCKET_NAME, Key=CAMINHO_NO_BUCKET)
conteudo_csv = response["Body"].read().decode("utf-8")

df = pd.read_csv(StringIO(conteudo_csv))

print(df.shape)
print(df.head())