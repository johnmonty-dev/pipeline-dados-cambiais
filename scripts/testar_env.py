from dotenv import load_dotenv
import os

load_dotenv()

variaveis = [
    'DB_HOST',
    'DB_PORT',
    'DB_NAME',
    'DB_USER',
    'DB_PASSWORD',
    'EMAIL_REMETENTE',
    'EMAIL_SENHA_APP',
    'EMAIL_SMTP_SERVER',
    'EMAIL_SMTP_PORT',
    'EMAIL_DESTINATARIO'
]

for nome in variaveis:
    valor = os.getenv(nome)
    if valor:
        print(nome, '-> OK (tamanho:', len(valor), 'caracteres)')
    else:
        print(nome, '-> FALTANDO OU VAZIO')
