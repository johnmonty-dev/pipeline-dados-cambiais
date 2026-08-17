import requests
import pandas as pd

url = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados?formato=json&dataInicial=01/01/2024&dataFinal=31/12/2024'

resposta = requests.get(url)
dados = resposta.json()

print('Status da requisição:', resposta.status_code)
print('Quantidade de registros recebidos:', len(dados))
print(dados)

df_dolar = pd.DataFrame(dados)

print(df_dolar.head(10))
print(df_dolar.dtypes) 