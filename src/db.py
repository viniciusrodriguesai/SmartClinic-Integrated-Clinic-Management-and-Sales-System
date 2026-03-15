import os
from contextlib import contextmanager
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / "secreto.env"

load_dotenv(ENV_PATH)


def _get_env(nome_variavel: str) -> str:

    valor = os.getenv(nome_variavel)

    if not valor:
        raise RuntimeError(f"Variável de ambiente ausente: {nome_variavel}")

    return valor


@contextmanager
def get_conn():

    conn = None

    try:
        conn = mysql.connector.connect(
            host=_get_env("DB_HOST"),
            port=int(_get_env("DB_PORT")),
            user=_get_env("DB_USER"),
            password=_get_env("DB_PASSWORD"),
            database=_get_env("DB_NAME"),
        )

        yield conn

    finally:

        if conn and conn.is_connected():
            conn.close()