import os
from contextlib import contextmanager

import mysql.connector
from dotenv import load_dotenv


# Carrega as variáveis do arquivo secreto.env
load_dotenv("secreto.env")


def _get_env(nome_variavel: str) -> str:
    """
    Busca uma variável de ambiente e lança erro se ela não existir.
    """
    valor = os.getenv(nome_variavel)
    if not valor:
        raise RuntimeError(f"Variável de ambiente ausente: {nome_variavel}")
    return valor


@contextmanager
def get_conn():
    """
    Abre uma conexão com o MySQL e garante que ela será fechada no final.
    Uso:
        with get_conn() as conn:
            ...
    """
    conn = None
    try:
        conn = mysql.connector.connect(
            host=_get_env("DB_HOST"),
            user=_get_env("DB_USER"),
            password=_get_env("DB_PASSWORD"),
            database=_get_env("DB_NAME"),
        )
        yield conn
    finally:
        if conn is not None and conn.is_connected():
            conn.close()