# AGI Tools

Biblioteca Python para facilitar operações de Data Lake, Spark, envio de e-mails corporativos e manipulação de configurações em projetos de dados.

## Funcionalidades

- **Spark Integration**: Criação, configuração e destruição de sessões Spark, inserção de dados em Data Lake, controle de métricas e checkpoints.
- **Mail**: Envio de e-mails via Microsoft Graph API, com suporte a múltiplos destinatários, CC, rodapé customizado e autenticação segura.
- **Configuração**: Carregamento centralizado de arquivos de configuração TOML, com tratamento de erros e timezone Brasil.
- **Teams**: Envio de mensagens para canais do Microsoft Teams via webhook, com personalização de cor, título e mensagem.

## Instalação

```bash
pip install agi-tools
```

## Uso Básico

### Spark

```python
from agi_tools.spark import AgiTools
agi = AgiTools()
spark = agi.create_spark_session('nome_da_sessao')
# ...processamento...
agi.insert_into_lake(
    data=spark.sql(query),
    write_mode='overwrite',
    partition_by='date_partition'
)
agi.destroy_spark_session()
```

### Envio de E-mail

```python
from agi_tools.mail import AgiMail
mail = AgiMail()
mail.send_email(
    subject="Assunto",
    mail_to=["destino@empresa.com"],
    html_body="<h1>Mensagem</h1>",
    mail_cc=["copia@empresa.com"]
)
```

### Teams

```python
from agi_tools.teams import AgiTeams
teams = AgiTeams()
teams.process_message(
    message_type='success',
    process_name='Processo de ETL'
)
# Ou envie uma mensagem personalizada:
teams.send_message(
    title='Alerta',
    color='#FF0000',
    message='Falha no processamento do ETL.'
)
```

### Configuração

```python
from agi_tools.tools import get_config
config = get_config('config')
```

### Semaphore

```python
from agi_tools.semaphore import AgiSemaphore
from agi_tools.spark import AgiTools

# Inicialização
agi = AgiTools()
spark = agi.create_spark_session('nome_da_sessao')
semaphore = AgiSemaphore(spark)

# put_semaphore: Atualiza o status do semáforo
semaphore.put_semaphore('nome_do_semaphore')

# get_last_updated: Retorna a data/hora da última atualização de uma tabela
ultima_atualizacao = semaphore.get_last_updated('database.tabela')

# get_semaphore: Lê o status do semáforo salvo em arquivo parquet
status = semaphore.get_semaphore('nome_do_semaphore')
print(status)
```

## Requisitos

- Python >= 3.9
- Spark (cluster ou local)
- Microsoft Graph API para envio de e-mails

## Licença

MIT
