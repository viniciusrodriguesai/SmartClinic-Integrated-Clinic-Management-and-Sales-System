from dataclasses import dataclass
from typing import List, Optional

from mysql.connector import Error
from db import get_conn


@dataclass(frozen=True)
class Cliente:
    id_cliente: int
    nome: str
    cpf: str
    telefone: Optional[str]
    email: str
    data_nascimento: Optional[str]


class ClienteDAO:

    @staticmethod
    def inserir(nome, cpf, telefone, email, data_nascimento) -> int:
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
                raise RuntimeError(f"Erro ao inserir cliente: {e}")

            finally:
                if cursor:
                    cursor.close()

    @staticmethod
    def alterar(id_cliente, nome, cpf, telefone, email, data_nascimento) -> int:
        sql = """
        UPDATE cliente
        SET nome=%s, cpf=%s, telefone=%s, email=%s, data_nascimento=%s
        WHERE id_cliente=%s
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
                raise RuntimeError(f"Erro ao alterar cliente: {e}")

            finally:
                if cursor:
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
            cursor = None
            try:
                cursor = conn.cursor()

                cursor.execute(sql, (f"%{parte_nome}%",))

                resultados = cursor.fetchall()

                return [Cliente(*linha) for linha in resultados]

            except Error as e:
                raise RuntimeError(f"Erro ao pesquisar cliente: {e}")

            finally:
                if cursor:
                    cursor.close()

    @staticmethod
    def remover(id_cliente: int) -> int:

        sql = """
        DELETE FROM cliente
        WHERE id_cliente = %s
        """

        with get_conn() as conn:
            cursor = None
            try:
                cursor = conn.cursor()

                cursor.execute(sql, (id_cliente,))

                conn.commit()

                return int(cursor.rowcount)

            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Erro ao remover cliente: {e}")

            finally:
                if cursor:
                    cursor.close()

    @staticmethod
    def listar_todos() -> List[Cliente]:

        sql = """
        SELECT id_cliente, nome, cpf, telefone, email, data_nascimento
        FROM cliente
        ORDER BY nome
        """

        with get_conn() as conn:
            cursor = None
            try:
                cursor = conn.cursor()

                cursor.execute(sql)

                resultados = cursor.fetchall()

                return [Cliente(*linha) for linha in resultados]

            except Error as e:
                raise RuntimeError(f"Erro ao listar clientes: {e}")

            finally:
                if cursor:
                    cursor.close()

    @staticmethod
    def buscar_por_id(id_cliente: int) -> Optional[Cliente]:

        sql = """
        SELECT id_cliente, nome, cpf, telefone, email, data_nascimento
        FROM cliente
        WHERE id_cliente = %s
        """

        with get_conn() as conn:
            cursor = None
            try:
                cursor = conn.cursor()

                cursor.execute(sql, (id_cliente,))

                resultado = cursor.fetchone()

                if resultado:
                    return Cliente(*resultado)

                return None

            except Error as e:
                raise RuntimeError(f"Erro ao buscar cliente: {e}")

            finally:
                if cursor:
                    cursor.close()