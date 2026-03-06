from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from mysql.connector import Error

from db import conectar, get_conn


@dataclass(frozen=True)
class Cliente:
    id_cliente: int
    nome: str
    cpf: str
    telefone: Optional[str]
    email: str
    data_nascimento: Optional[str]  # formato "YYYY-MM-DD"


class ClienteDAO:
    """
    Camada de acesso a dados (DAO) para a tabela cliente.
    """

    @staticmethod
    def inserir(nome: str, cpf: str, telefone: Optional[str], email: str, data_nascimento: Optional[str]) -> int:
        sql = """
        INSERT INTO cliente (nome, cpf, telefone, email, data_nascimento)
        VALUES (%s, %s, %s, %s, %s)
        """

        conn = conectar()
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (nome, cpf, telefone, email, data_nascimento))
                conn.commit()
                return int(cursor.lastrowid)
            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Erro ao inserir cliente: {e}") from e
            finally:
                cursor.close()

    @staticmethod
    def alterar(
        id_cliente: int,
        nome: str,
        cpf: str,
        telefone: Optional[str],
        email: str,
        data_nascimento: Optional[str],
    ) -> int:
        sql = """
        UPDATE cliente
        SET nome = %s,
            cpf = %s,
            telefone = %s,
            email = %s,
            data_nascimento = %s
        WHERE id_cliente = %s
        """

        with get_conn() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (nome, cpf, telefone, email, data_nascimento, id_cliente))
                conn.commit()
                return int(cursor.rowcount)  # quantas linhas foram alteradas
            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Erro ao alterar cliente: {e}") from e
            finally:
                cursor.close()

    @staticmethod
    def pesquisar_por_nome(parte_nome: str) -> List[Cliente]:
        sql = """
        SELECT id_cliente, nome, cpf, telefone, email, data_nascimento
        FROM cliente
        WHERE nome LIKE %s
        ORDER BY nome
        """

        with get_conn() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, (f"%{parte_nome}%",))
                rows = cursor.fetchall()
                return [Cliente(*row) for row in rows]
            finally:
                cursor.close()