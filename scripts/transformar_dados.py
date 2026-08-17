import requests
import pandas as pd

url = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados?formato=json&dataInicial=01/01/2024&dataFinal=31/12/2024'
resposta = requests.get(url)
dados = resposta.json()
df = pd.DataFrame(dados)

print('Dados brutos:')
print(df.head())
print(df.dtypes)

df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')

df['valor'] = df['valor'].astype(float)

print('')
print('Dados apos conversao de tipos:')
print(df.head())
print(df.dtypes)

df = df.sort_values('data').reset_index(drop=True)

df['variacao_percentual'] = df['valor'].pct_change() * 100

print('')
print('Dados com variacao percentual:')
print(df.head(10))

print('')
print('Estatisticas da variacao percentual:')
print(df['variacao_percentual'].describe())