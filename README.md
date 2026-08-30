# Pipeline de Dados Cambiais: Cotação do Dólar

**Stack:** Python, PostgreSQL, SQLAlchemy, Requests, SMTP

Esse projeto é um pipeline de ETL (extração, transformação e carga) que busca a cotação do dólar direto na API pública do Banco Central, limpa e organiza os dados, salva tudo num banco PostgreSQL e manda um e mail automático se algum dia tiver uma variação fora do normal.

## Como funciona, no geral

```
API do Banco Central  →  Extração  →  Limpeza/Transformação  →  PostgreSQL  →  Detecção de anomalia  →  E mail de alerta
```

1. Puxo os dados direto da API do BCB (o SGS, sistema deles de séries históricas), pegando a série do dólar comercial. Não precisa cadastro nem chave, é só chamar a URL.
2. Limpo os dados: a API manda tudo como texto, então converto a data pra data de verdade e o valor pra número, e calculo quanto o dólar variou de um dia pro outro em porcentagem.
3. Salvo essa tabela já tratada dentro de um banco PostgreSQL, numa tabela chamada `cotacao_dolar`.
4. Calculo a média e o desvio padrão dessa variação diária ao longo do ano, e uso isso pra definir o que é um dia "fora do padrão" (mais de 2 desvios padrão longe da média).
5. Se encontrar algum dia assim, monto um e mail com a lista desses dias e mando automaticamente.

## Os números que saíram

- 253 dias de cotação processados (ano de 2024).
- A variação diária fica em média em 0,096%, então bem perto de zero.
- O desvio padrão é de 0,70%.
- Com isso, qualquer dia que passar de mais ou menos 1,3% a 1,5% conta como anomalia.
- No total apareceram 17 dias assim, sendo o maior deles em 28/11/2024 (subiu 2,71% num dia só) e o de maior queda em 06/08/2024 (caiu quase 2%).

## Um perrengue real que tive no meio do caminho

Comecei configurando o envio de e mail pelo Outlook, mas descobri no meio do processo que a Microsoft parou de aceitar login simples (usuário e senha, mesmo usando senha de aplicativo) pra mandar e mail via código. Eles exigem um sistema mais complexo de autenticação (OAuth2) que ficaria grande demais pra esse projeto. Resolvi trocando o remetente pra uma conta Gmail, mantendo o Outlook só como quem recebe o alerta. Achei importante deixar isso registrado porque foi um problema de verdade que apareceu do nada, e serve de lição: às vezes um serviço externo muda a regra do jogo e você precisa se adaptar no meio do projeto.

## Como o projeto está organizado

```
pipeline-etl/
├── data/                      (não sobe pro github, é só local)
├── logs/                      (idem)
├── scripts/
│   ├── testar_conexao.py      só pra testar se o Python conversa com o banco
│   ├── extrair_api.py         primeiro rascunho da parte de puxar dados da API
│   ├── transformar_dados.py   limpeza e cálculo da variação percentual
│   ├── carregar_dados.py      junta extração, limpeza e manda pro banco
│   └── detectar_anomalias.py  o pipeline inteiro, do início até o e mail
├── .env                       (credenciais, não sobe pro github)
├── .gitignore
├── requirements.txt
└── README.md
```

## Variáveis que você precisa configurar (arquivo .env)

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pipeline_etl
DB_USER=postgres
DB_PASSWORD=sua_senha_do_postgres

EMAIL_REMETENTE=seu_email@gmail.com
EMAIL_SENHA_APP=sua_senha_de_app_de_x_caracteres
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_DESTINATARIO=email_que_vai_receber_o_alerta@qualquerprovedor.com
```

A senha de app do Gmail você gera em myaccount.google.com/apppasswords, precisa ter a verificação em duas etapas ativada primeiro.

## Pra rodar na sua máquina

```bash
python -m venv venv
source venv/bin/activate        # no Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Depois é só criar um banco PostgreSQL local chamado `pipeline_etl` (ou mudar o nome no .env), preencher as credenciais e rodar:

```bash
python scripts/detectar_anomalias.py
```

Esse script sozinho já faz tudo: busca os dados de 2024, limpa, carrega no banco e manda o e mail se achar alguma anomalia.

## O que eu ainda quero melhorar

- Fazer isso rodar sozinho de tempos em tempos, em vez de eu precisar executar na mão.
- Adicionar uma segunda fonte de dados, tipo um CSV local, pra treinar a parte de juntar fontes diferentes.
- Voltar e resolver o envio pelo Outlook direito, usando OAuth2 dessa vez.
- Deixar o período de datas configurável, em vez de fixo em 2024.
- Guardar logs de cada execução na pasta logs, em vez de só mostrar no terminal.
