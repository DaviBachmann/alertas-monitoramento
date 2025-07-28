# encoding: utf-8

# Importa as bibliotecas necessárias
import pyodbc
import time
import os
import pandas as pd
from datetime import datetime

from core.db_utils import executar_query
from core.email_utils import enviar_email

def verificas_contingencia(
    conn: pyodbc.Connection, # Objeto de conexão com o banco de dados
    smtp_info: dict, # Dicionário com as informações do servidor SMTP (servidor, porta, usuário e senha)
    destinatario: str # Endereço de e-mail do destinatário
) -> None:
    
    """
    Desc:
    Esta função verifica as filiais em contingência 
    
    Args:
    - conn: pyodbc.Connection, conexão com o banco de dados
    - smtp_info: dict, dicionário contendo informações do servidor SMTP
    - destinatario: string, endereço de e-mail do destinatário
    
    Returns:
    - None
    
    Raises:
    - Exception: se ocorrer um erro ao enviar o e-mail
    
    Example:
    verificar_tarefas_datalog(
        conn=pyodbc.connect('Driver={SQL Server};Server=servidor;Database=database;UID=user;PWD=password'),
        smtp_info={
            "SMTP_SERVER": "smtp.exemplo.com",
            "SMTP_PORT": 587,
            "EMAIL_USER":
        }
    )
    
    Obs:
    - Certifique-se de que a conexão com o banco de dados esteja ativa.
    - A consulta SQL pode ser ajustada conforme necessário para atender aos requisitos específicos.
    - O envio de e-mail requer que as informações SMTP estejam corretas.
    """
    
    # Carrega as variáveis de ambiente do arquivo .env
    # Query para verificar tarefas pendentes no banco de dados
    query = os.getenv("query")

    # Executa a consulta no banco de dados e obtém os resultados
    resultados, colunas = executar_query(conn, query, fetch=True)
    resultados = [tuple(row) for row in resultados]
    
    df_resultados = pd.DataFrame(resultados, columns=colunas)
    
    # Verifica se há resultados e envia o e-mail
    if resultados:
        
        corpo = (
            f"Rotina de monitoramento contingência VIVO NFCe ({len(resultados)} filiais em contingência)\n\n"
            "Segue relação de filiais que estão em contingência a mais de um dia:\n\n"
            + "Este e-mail é gerado automaticamente, favor não responder."
        )
        assunto = "AVISO - Verificação de Contingência - VIVO"
        
        for i in range(10):
            if enviar_email(destinatario=destinatario,
                            assunto=assunto,
                            corpo=corpo,
                            smtp_info=smtp_info,
                            anexo_temp=df_resultados,
                            nome_arquivo_temp="contingencia_vivo",
                            tipo_arquivo_temp=".xlsx"):
                break
            time.sleep(5)
        else:
            print(f"Falha ao enviar e-mail após 10 tentativas. {datetime.now()}")
            
    else:
        print(f'Não há agentes em contingência. {datetime.now()}')