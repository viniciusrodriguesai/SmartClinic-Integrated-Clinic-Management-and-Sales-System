from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator, Optional

import mysql.connector
from mysql.connector import MySQLConnection
from dotenv import load_dotenv

load_dotenv()


def _get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Variável de ambiente ausente: {name}")
    return value


@contextmanager
def get_conn() -> Iterator[MySQLConnection]:
    """
    Abre uma conexão com o MySQL e garante fechamento, mesmo se der erro.
    Use: with get_conn() as conn: ...
    """
    conn: Optional[MySQLConnection] = None
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