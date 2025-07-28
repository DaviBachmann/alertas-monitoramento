# encoding: utf-8

# Importa as bibliotecas necessárias
import pyodbc
import re

def conectar_banco(
    server: str,
    database: str,
    username: str,
    password: str
) -> pyodbc.Cursor:
    
    """
    Desc:
    Esta função conecta ao banco de dados SQL Server usando o pyodbc.
    
    Args:
    - server (string): Nome do servidor SQL Server.
    - databas (string): Nome do database.
    - username (string): Nome de usuário para autenticação.
    - password (string): Senha para autenticação.
    
    Returns:
    - conn (pyodbc.Connection): Objeto de conexão com o banco de dados.
    
    Raises:
    - pyodbc.Error: Se ocorrer um erro ao conectar ao banco de dados.
    
    Example:
    conn = conectar_banco("servidor", "database", "usuario", "senha")
    
    Obs:
    - Certifique-se de que o driver ODBC esteja instalado e configurado corretamente.
    - A função assume que o servidor SQL Server está acessível e em execução.
    
    """
    
    # Conecta ao banco de dados usando o pyodbc com uma string de conexão
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password}"
    )
    
    return conn

def executar_query(
    conn: pyodbc.Connection,
    query: str,
    fetch: bool = False,
    commit: bool = False,
    params: tuple | str | None = None
) -> tuple[list[tuple], list[str]]:
    
    """
    Desc:
    Esta função executa uma query SQL no banco de dados.
    
    Args:
    - conn (pyodbc.Connection): Objeto de conexão com o banco de dados.
    - query (string): A query SQL a ser executada.
    
    Returns:
    - resultados (list[tuple]): Lista de tuplas com os resultados da query.
    - colunas (list[str]): Lista de strings com os nomes das colunas retornadas.
    
    Raises:
    - pyodbc.Error: Se ocorrer um erro ao executar a query.
    
    Example:
    resultados, colunas = executar_query(
        conn=pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        ),
        "SELECT TOP 5 * FROM tabela"
    )
    
    Obs:
    - Certifique-se de que a conexão com o banco de dados esteja ativa.
    - A função assume que a query retornará resultados.
    """
        
    try:
        with conn.cursor() as cursor:
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                resultados = cursor.fetchall()
                colunas = [desc[0] for desc in cursor.description]
                return resultados, colunas
            
            if commit:
                conn.commit()
                
    except pyodbc.IntegrityError as e:
        if len(e.args) > 1:
            msg = e.args[1]
            
        match = re.search(r"The duplicate key value is \((.*?)\)", msg)
        if match:
            valor_duplicado = match.group(1)
            print(f"Valor duplicado: {valor_duplicado}")
            
        conn.rollback()
        return False

    except pyodbc.Error as e:
        print(f"Erro do banco: {e.args[1]}")
        conn.rollback()
        return False

    except Exception as e:
        print(f"Erro inesperado: {e}")
        conn.rollback()
        return False

    return [], []

def fechar_conexao(
    conexao: pyodbc.Connection
) -> None:
    
    """
    Desc:
    Esta função fecha a conexão com o banco de dados.
    
    Args:
    - conexao (pyodbc.Connection): Objeto de conexão com o banco de dados.
    
    Returns:
    - None
    
    Raises:
    - pyodbc.Error: Se ocorrer um erro ao fechar a conexão.
    
    Example:
    fechar_conexao(
        conn=pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )
    )
    
    Obs:
    - Certifique-se de que todas as operações no banco de dados estejam concluídas antes de fechar a conexão.
    """
    
    conexao.close()