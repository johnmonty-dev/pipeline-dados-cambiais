import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

url = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados?formato=json&dataInicial=01/01/2024&dataFinal=31/12/2024'
resposta = requests.get(url)
dados = resposta.json()
df = pd.DataFrame(dados)

df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
df['valor'] = df['valor'].astype(float)
df = df.sort_values('data').reset_index(drop=True)
df['variacao_percentual'] = df['valor'].pct_change() * 100

print('Dados prontos para carga:')
print(df.head())
print('Total de linhas:', len(df))

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

url_conexao = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(url_conexao)

df.to_sql('cotacao_dolar', engine, if_exists='replace', index=False)

print('')
print('Dados carregados com sucesso na tabela cotacao_dolar!')
