# encoding: utf-8

# Importa as bibliotecas necessárias
import pyodbc
import time
import os
import pandas as pd
from datetime import datetime

from core.db_utils import executar_query
from core.email_utils import enviar_email

def verificar_notas(
    conn: pyodbc.Connection, # Objeto de conexão com o banco de dados
    smtp_info: dict, # Dicionário com as informações do servidor SMTP (servidor, porta, usuário e senha)
    destinatario: str # Endereço de e-mail do destinatário
) -> None:
    
    """
    Desc:
    Função para verificar notas fiscais eletrônicas (NFe) que não foram manifestadas automaticamente.
    
    Args:
    - conn: Objeto de conexão com o banco de dados.
    - smtp_info: Dicionário com as informações do servidor SMTP (servidor, porta, usuário e senha).
    - destinatario: Endereço de e-mail do destinatário.

    Returns:
    - None

    Raises:
    - pyodbc.Error: Se ocorrer um erro ao executar a consulta no banco de dados.

    Example:
    verificar_notas(
        conn=pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        ),
        smtp_info={
            "smtp_server": "smtp.exemplo.com",
            "smtp_port": 587,
            "email_from": "email@exemplo.com.br"
        }
    )
    
    Obs:
    - Certifique-se de que a conexão com o banco de dados esteja ativa.
    - A consulta SQL pode ser ajustada conforme necessário para atender aos requisitos específicos.
    - O envio de e-mail requer que as informações SMTP estejam corretas.
    """
    
    # Carrega as variáveis de ambiente do arquivo .env
    # Query para verificar tarefas pendentes no banco de dados
    query = os.getenv('query')

    # Executa a consulta no banco de dados e obtém os resultados
    resultados, colunas = executar_query(conn, query, fetch=True)
    resultados = [tuple(row) for row in resultados]
    df_resultados = pd.DataFrame(resultados, columns=colunas)
    
    # Verifica se há resultados e envia o e-mail
    if resultados:
        
        corpo = (
            f"Rotina de monitoramento manifestação NFe ({len(resultados)} não manifestadas)\n\n"
            "Segue relação de notas que não realizaram a manifestação automática:\n\n"
            + "Este e-mail é gerado automaticamente, favor não responder."
        )
        assunto = f"AVISO - Nissei - NOTAS SEM MANIFESTAÇÃO NFe - {datetime.now()}"
                
        for i in range(10):
            if enviar_email(destinatario=destinatario,
                            assunto=assunto,
                            corpo=corpo,
                            smtp_info=smtp_info,
                            anexo_temp=df_resultados,
                            nome_arquivo_temp="notas",
                            tipo_arquivo_temp=".xlsx"):
                break
            time.sleep(5)
        else:
            print(f"Falha ao enviar e-mail após 10 tentativas. {datetime.now()}")

    else:
        print(f'Não há notas sem manifestação. {datetime.now()}')
