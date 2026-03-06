from dataclasses import dataclass
from typing import List, Optional

from mysql.connector import Error

from db import get_conn


@dataclass(frozen=True)
class Cliente:
    """
    Representa um cliente da clínica.
    """
    id_cliente: int
    nome: str
    cpf: str
    telefone: Optional[str]
    email: str
    data_nascimento: Optional[str]


class ClienteDAO:
    """
    Classe responsável pelas operações de acesso ao banco
    relacionadas à tabela cliente.
    """

    @staticmethod
    def inserir(
        nome: str,
        cpf: str,
        telefone: Optional[str],
        email: str,
        data_nascimento: Optional[str],
    ) -> int:
        """
        Insere um cliente no banco e retorna o id gerado.
        """
        sql = """
        INSERT INTO cliente (nome, cpf, telefone, email, data_nascimento)
        VALUES (%s, %s, %s, %s, %s)
        """

        with get_conn() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (nome, cpf, telefone, email, data_nascimento))
                conn.commit()
                return int(cursor.lastrowid)
            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Erro ao inserir cliente: {e}") from e
            finally:
                if cursor is not None:
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
        """
        Altera um cliente existente e retorna a quantidade de linhas alteradas.
        """
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
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute(
                    sql,
                    (nome, cpf, telefone, email, data_nascimento, id_cliente),
                )
                conn.commit()
                return int(cursor.rowcount)
            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Erro ao alterar cliente: {e}") from e
            finally:
                if cursor is not None:
                    cursor.close()

    @staticmethod
    def pesquisar_por_nome(parte_nome: str) -> List[Cliente]:
        """
        Pesquisa clientes por nome usando LIKE e retorna
        uma lista de objetos Cliente.
        """
        sql = """
        SELECT id_cliente, nome, cpf, telefone, email, data_nascimento
        FROM cliente
        WHERE nome LIKE %s
        ORDER BY nome
        """

        with get_conn() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (f"%{parte_nome}%",))
                resultados = cursor.fetchall()
                return [Cliente(*linha) for linha in resultados]
            except Error as e:
                raise RuntimeError(f"Erro ao pesquisar cliente por nome: {e}") from e
            finally:
                if cursor is not None:
                    cursor.close()