# encoding: utf-8

# Importa as bibliotecas necessárias
import os
import tempfile

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def enviar_email(
    destinatario: str, # Endereço de e-mail do destinatário
    assunto: str, # Assunto do e-mail
    corpo: str, # Corpo do e-mail
    smtp_info: dict, # Dicionário com as informações do servidor SMTP (servidor, porta, usuário e senha)
    anexos: list = None, # Lista de anexos (opcional)
    anexo_temp: any = None, # Conteúdo do arquivo temporário (opcional)
    nome_arquivo_temp: str = "notas", # Nome do arquivo temporário (opcional)
    tipo_arquivo_temp: str = ".txt" # Tipo do arquivo temporário (opcional)
) -> bool:
    
    """
    Desc:
    Esta função envia um e-mail utilizando o servidor SMTP especificado.
    
    Args:
    - destinatario (string): Endereço de e-mail do destinatário.
    - assunto (string): Assunto do e-mail.
    - corpo (string): Corpo do e-mail.
    - smtp_info (dict): Dicionário contendo informações do servidor SMTP.
    - anexos (list[str], opcional): Lista de caminhos para arquivos a serem anexados.
    - anexo_temp (any, opcional): Conteúdo do arquivo temporário a ser anexado.
    - nome_arquivo_temp (string, opcional): Nome do arquivo temporário (sem extensão).
    - tipo_arquivo_temp (string, opcional): Tipo do arquivo temporário (extensão).
    
    Returns:
    - bool: True se o e-mail foi enviado com sucesso, False caso contrário.
    
    Raises:
    - smtplib.SMTPException: Se ocorrer um erro ao enviar o e-mail.
    
    Example:
    enviar_email(
        destinatario="email@exemplo.com.br",
        assunto="Teste de E-mail",
        corpo="Este é um teste de e-mail.",
        smtp_info={
            "SMTP_SERVER": "smtp.exemplo.com",
            "SMTP_PORT": 587,
            "EMAIL_USER": "usuario@exemplo.com.br"
        }
    )
    
    Obs:
    - Certifique-se de que o servidor SMTP esteja acessível e em execução.
    - A função assume que as credenciais de autenticação estão corretas.
    """
    
    try:
        # Configurações do servidor SMTP
        msg = MIMEMultipart()
        msg["From"] = smtp_info["email_from"]
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.attach(MIMEText(corpo, "plain"))
        
        # Anexa arquivos temporários se fornecidos
        if anexo_temp is not None:
            
            # Gera um arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix=tipo_arquivo_temp) as temp_file:
                temp_file_path = temp_file.name
                
            print(f"Arquivo temporário criado: {temp_file_path}")
            
            # Verifica o tipo de arquivo e escreve o conteúdo
            if tipo_arquivo_temp == ".xlsx":
                
                anexo_temp.to_excel(temp_file_path, index=False)
                mime_subtype = "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
            elif tipo_arquivo_temp == ".txt":
                
                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(anexo_temp.encode('utf-8') if isinstance(anexo_temp, str) else anexo_temp)
                mime_subtype = "octet-stream"
            
            # Anexa o arquivo temporário ao e-mail
            with open(temp_file_path, "rb") as temp_file:
                parte = MIMEBase("application", mime_subtype)
                parte.set_payload(temp_file.read())
            encoders.encode_base64(parte)
            parte.add_header(
                "Content-Disposition",
                f"attachment; filename={nome_arquivo_temp+tipo_arquivo_temp}"
            )
            msg.attach(parte)
        
        # Anexa arquivos adicionais se fornecidos
        if anexos is not None:
            
            # Iterar sobre os arquivos e anexá-los
            for caminho_arquivo in anexos:
                if os.path.isfile(caminho_arquivo):
                    
                    # Anexa o arquivo ao e-mail
                    with open(caminho_arquivo, "rb") as arquivo:
                        parte = MIMEBase("application", "octet-stream")
                        parte.set_payload(arquivo.read())
                        
                    encoders.encode_base64(parte)
                    parte.add_header(
                        "Content-Disposition",
                        f"attachment; filename={os.path.basename(caminho_arquivo)}"
                    )
                    msg.attach(parte)
                    
                else:
                    print(f"Arquivo {caminho_arquivo} não encontrado. Anexo não adicionado.")
        
        print("Email configurado com sucesso.")
        
        # Envio
        try:
            
            # Conecta ao servidor SMTP
            with smtplib.SMTP(smtp_info["smtp_server"], int(smtp_info["smtp_port"])) as server:
                print("Servidor SMTP conectado com sucesso.") 
                
                # Inicia a conexão TLS se o servidor suportar
                server.starttls()
                print("Conexão TLS iniciada com sucesso.")
            
                # Realiza o login no servidor SMTP
                server.login(smtp_info["email_from"], smtp_info["email_password"])
                print("Login no servidor SMTP realizado com sucesso.")

                # Envia o e-mail
                server.sendmail(smtp_info["email_from"], destinatario, msg.as_string())
                print("Email enviado com sucesso.")
                
        except smtplib.SMTPException as e:
            
            print(f"Erro ao enviar o e-mail --: {e}")
            return False

        return True

    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False