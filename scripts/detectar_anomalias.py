import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

url = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados?formato=json&dataInicial=01/01/2024&dataFinal=31/12/2024'
resposta = requests.get(url)
dados = resposta.json()
df = pd.DataFrame(dados)

df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
df['valor'] = df['valor'].astype(float)
df = df.sort_values('data').reset_index(drop=True)
df['variacao_percentual'] = df['valor'].pct_change() * 100

print('Dados prontos. Total de linhas:', len(df))

media = df['variacao_percentual'].mean()
desvio_padrao = df['variacao_percentual'].std()

limite_superior = media + (2 * desvio_padrao)
limite_inferior = media - (2 * desvio_padrao)

print('')
print('Limite superior de anomalia:', round(limite_superior, 2), '%')
print('Limite inferior de anomalia:', round(limite_inferior, 2), '%')

anomalias = df[(df['variacao_percentual'] > limite_superior) | (df['variacao_percentual'] < limite_inferior)]

print('')
print('Quantidade de dias anômalos encontrados:', len(anomalias))
print(anomalias[['data', 'valor', 'variacao_percentual']])

EMAIL_REMETENTE = os.getenv('EMAIL_REMETENTE')
EMAIL_SENHA_APP = os.getenv('EMAIL_SENHA_APP')
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT'))

EMAIL_DESTINATARIO = os.getenv('EMAIL_DESTINATARIO')

if len(anomalias) > 0:
    corpo_email = 'Foram detectados ' + str(len(anomalias)) + ' dias com variacao anomala na cotacao do dolar:\n\n'

    for index, linha in anomalias.iterrows():
        data_formatada = linha['data'].strftime('%d/%m/%Y')
        corpo_email += 'Data: ' + data_formatada + ' | Valor: R$ ' + str(round(linha['valor'], 4)) + ' | Variacao: ' + str(round(linha['variacao_percentual'], 2)) + '%\n'

    print('')
    print('Corpo do email que sera enviado:')
    print(corpo_email)

    mensagem = MIMEMultipart()
    mensagem['From'] = EMAIL_REMETENTE
    mensagem['To'] = EMAIL_DESTINATARIO
    mensagem['Subject'] = 'Alerta: Anomalias detectadas na cotacao do dolar'
    mensagem.attach(MIMEText(corpo_email, 'plain'))

    try:
        servidor = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        servidor.starttls()
        servidor.login(EMAIL_REMETENTE, EMAIL_SENHA_APP)
        servidor.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, mensagem.as_string())
        servidor.quit()
        print('')
        print('Email enviado com sucesso!')
    except Exception as erro:
        print('')
        print('Erro ao enviar email:', erro)
else:
    print('Nenhuma anomalia encontrada, email nao sera enviado.')


