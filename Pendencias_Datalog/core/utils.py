import os
import urllib.request
import sys
from dotenv import load_dotenv

# FUNCOES AUXILIARES E DE UTILIDADES

def limpa_tela():
    _ = os.system('cls' if os.name == 'nt' else 'clear')

def menu(
    opcoes: dict, 
    mensagem: str = None
):
    if mensagem:
        print(mensagem)
    escolha = input('>> ')
    
    while True:
        if escolha in opcoes:
            
            if opcoes[escolha] == 'Outro':
                return input(': ')
            
            if callable(opcoes[escolha]):
                return opcoes[escolha]()
            
            else:
                return opcoes[escolha]
            
        else:
            escolha = input(f'Escolha inválida ({escolha}). Por favor, informe novamente: ')

def verificar_conexao():
    try:
        urllib.request.urlopen('https://www.google.com', timeout=5)
        return True
    except:
        return False
    
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def carregar_arquivo_env():
    base_path = get_base_path()
    
    external_env_path = os.path.join(base_path, '.env')
    
    if os.path.exists(external_env_path):
        load_dotenv(dotenv_path=external_env_path)
    else:
        embedded_path = os.path.join(sys._MEIPASS, '.env') if getattr(sys, 'frozen', False) else None
        if embedded_path and os.path.exists(embedded_path):
            load_dotenv(dotenv_path=embedded_path)