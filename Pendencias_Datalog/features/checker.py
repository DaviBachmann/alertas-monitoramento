# encoding: utf-8

# Importa as bibliotecas necessárias
import pyodbc
import time
import os
import pandas as pd

from core.db_utils import executar_query
from core.email_utils import enviar_email
from datetime import datetime

def verificar_tarefas_datalog(
    conn: pyodbc.Connection, # Objeto de conexão com o banco de dados
    smtp_info: dict, # Dicionário com as informações do servidor SMTP (servidor, porta, usuário e senha)
    destinatario: str # Endereço de e-mail do destinatário
) -> None:
    
    # Carrega as variáveis de ambiente do arquivo.env
    # Query para verificar tarefas pendentes no banco de dados
    query = os.getenv("query")
    
    # Executa a consulta no banco de dados e transforma os resultados em um DataFrame
    resultados, colunas = executar_query(conn, query, fetch=True)
    resultados = [tuple(row) for row in resultados]
    df_resultados = pd.DataFrame(resultados, columns=colunas)

    # Verifica se há resultados e envia o e-mail
    if resultados:
        
        corpo = (
            f"Rotina de monitoramento Inventti x Datalog ({len(resultados)} Pendentes)\n\n"
            "Segue planilha em anexo com task's dos documentos que estão pendentes em nossa aplicação:\n\n"
            + "Este e-mail é gerado automaticamente, favor não responder."
        )
        assunto = f"AVISO - TASK'S PENDENTES INBOUNDNFSe {datetime.now()}"
        
        # Envia o e-mail com os resultados
        for i in range(10):
            if enviar_email(destinatario=destinatario,
                            assunto=assunto,
                            corpo=corpo,
                            smtp_info=smtp_info,
                            anexo_temp=df_resultados,
                            nome_arquivo_temp="tasks",
                            tipo_arquivo_temp=".xlsx"):
                break
            time.sleep(5)
            
        else:
            print(f"Falha ao enviar e-mail após 10 tentativas. {datetime.now()}")
            return False

    else:
        print(f'Não há documentos pendentes {datetime.now()}')