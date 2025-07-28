# encoding: utf-8

# Importa as bibliotecas necessárias
import os
import schedule
import time

from core.db_utils import conectar_banco, fechar_conexao
from features.checker import verificas_contingencia
from core.utils import carregar_arquivo_env

def main():
    
    """
    Função principal: carrega variáveis e executa verificação das tarefas.
    """
    
    # Carrega as variáveis de ambiente do arquivo .env
    try:
        carregar_arquivo_env()
        
    except Exception as e:
        print(f"Erro ao carregar variáveis de ambiente: {e}")
        
    db_server = os.getenv("db_server") # Servidor do banco de dados
    db_user = os.getenv("db_user") # Usuário do banco de dados
    db_password = os.getenv("db_password") # Senha do usuário
    db_name = os.getenv("db_name") # Nome do banco de dados
    
    try:
        # Conecta ao banco de dados
        conn = conectar_banco(db_server, db_name, db_user, db_password)
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    
    # Informações para o envio de e-mail
    smtp_info = {
        "smtp_server": os.getenv("smtp_server"),
        "smtp_port": os.getenv("smtp_port"),
        "email_from": os.getenv("email_from"),
        "email_password": os.getenv("email_password"),
    }
    destinatario = os.getenv("email_to")
    
    try:
        verificas_contingencia(
            conn=conn,
            smtp_info=smtp_info,
            destinatario=destinatario
        )
    except Exception as e:
        print(f"Erro ao verificar contingência: {e}")
        
    try:            
        fechar_conexao(conn)
    except Exception as e:
        print(f"Erro ao fechar a conexão com o banco de dados: {e}")
        
# Agendamento da rotina
horarios = [f"{hora:02d}:00" for hora in range(8, 18)]
dias_uteis = ["monday", "tuesday", "wednesday", "thursday", "friday"]

for dia in dias_uteis:
    for horario in horarios:
        getattr(schedule.every(), dia).at(horario).do(main)

# Loop de execução
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)