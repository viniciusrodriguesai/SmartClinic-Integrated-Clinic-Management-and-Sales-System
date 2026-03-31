from dataclasses import dataclass
from typing import List, Optional

from mysql.connector import Error
from db import get_conn

"""Definindo o dataclass Cliente para representar os dados de um cliente, 
com campos correspondentes às colunas da tabela cliente no banco de dados.
Os campos cidade, torce_flamengo e assiste_one_piece foram adicionados na Parte 2
para suporte às regras de desconto automático."""
@dataclass(frozen=True)
class Cliente:
    id_cliente: int
    nome: str
    cpf: str
    telefone: Optional[str]
    email: str
    data_nascimento: Optional[str]
    cidade: Optional[str] = None
    torce_flamengo: bool = False
    assiste_one_piece: bool = False

    @property
    def tem_desconto(self) -> bool:
        """Retorna True se o cliente tiver direito a 10% de desconto:
        torcedor do Flamengo, fã de One Piece ou morador de Sousa."""
        return (
            self.torce_flamengo or
            self.assiste_one_piece or
            (self.cidade or "").lower() == "sousa"
        )


"""Definindo a classe ClienteDAO para encapsular as operações de acesso a dados relacionadas aos clientes,
com métodos estáticos para inserir, alterar, pesquisar, remover e listar clientes, bem como um método para gerar um relatório do sistema
com base nos dados dos clientes"""
class ClienteDAO:

    @staticmethod
    def inserir(nome: str, cpf: str, telefone: Optional[str], email: str,
                data_nascimento: Optional[str], cidade: Optional[str] = None,
                torce_flamengo: bool = False, assiste_one_piece: bool = False) -> int:
        sql = """
        INSERT INTO cliente (nome, cpf, telefone, email, data_nascimento,
                             cidade, torce_flamengo, assiste_one_piece)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        with get_conn() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (nome, cpf, telefone, email, data_nascimento,
                                     cidade, int(torce_flamengo), int(assiste_one_piece)))
                conn.commit()
                return int(cursor.lastrowid)

            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Erro ao inserir cliente: {e}")

            finally:
                if cursor:
                    cursor.close()

    @staticmethod
    def alterar(id_cliente, nome, cpf, telefone, email, data_nascimento,
                cidade=None, torce_flamengo=False, assiste_one_piece=False) -> int:
        sql = """
        UPDATE cliente
        SET nome=%s, cpf=%s, telefone=%s, email=%s, data_nascimento=%s,
            cidade=%s, torce_flamengo=%s, assiste_one_piece=%s
        WHERE id_cliente=%s
        """
        with get_conn() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute(
                    sql,
                    (nome, cpf, telefone, email, data_nascimento,
                     cidade, int(torce_flamengo), int(assiste_one_piece), id_cliente),
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
        SELECT id_cliente, nome, cpf, telefone, email, data_nascimento,
               IFNULL(cidade, NULL),
               IFNULL(torce_flamengo, 0),
               IFNULL(assiste_one_piece, 0)
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
                # Convertendo os resultados em objetos Cliente,
                # garantindo os tipos corretos para os campos booleanos
                return [
                    Cliente(r[0], r[1], r[2], r[3], r[4],
                            str(r[5]) if r[5] else None,
                            r[6], bool(r[7]), bool(r[8]))
                    for r in resultados
                ]

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
        SELECT id_cliente, nome, cpf, telefone, email, data_nascimento,
               IFNULL(cidade, NULL),
               IFNULL(torce_flamengo, 0),
               IFNULL(assiste_one_piece, 0)
        FROM cliente
        ORDER BY nome
        """
        with get_conn() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                resultados = cursor.fetchall()
                return [
                    Cliente(r[0], r[1], r[2], r[3], r[4],
                            str(r[5]) if r[5] else None,
                            r[6], bool(r[7]), bool(r[8]))
                    for r in resultados
                ]

            except Error as e:
                raise RuntimeError(f"Erro ao listar clientes: {e}")

            finally:
                if cursor:
                    cursor.close()

    @staticmethod
    def buscar_por_id(id_cliente: int) -> Optional[Cliente]:
        sql = """
        SELECT id_cliente, nome, cpf, telefone, email, data_nascimento,
               IFNULL(cidade, NULL),
               IFNULL(torce_flamengo, 0),
               IFNULL(assiste_one_piece, 0)
        FROM cliente
        WHERE id_cliente = %s
        """
        with get_conn() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute(sql, (id_cliente,))
                resultado = cursor.fetchone()

                """Verificando se a consulta retornou um resultado e, em caso afirmativo, 
                criando um objeto Cliente a partir dos dados retornados."""
                if resultado:
                    return Cliente(resultado[0], resultado[1], resultado[2],
                                   resultado[3], resultado[4],
                                   str(resultado[5]) if resultado[5] else None,
                                   resultado[6], bool(resultado[7]), bool(resultado[8]))

                return None

            except Error as e:
                raise RuntimeError(f"Erro ao buscar cliente: {e}")

            finally:
                if cursor:
                    cursor.close()

    # Gerar relatório do sistema com totais de clientes e contagem por perfil
    @staticmethod
    def gerar_relatorio() -> dict:
        sql = """
        SELECT
            COUNT(*)                                        AS total_clientes,
            COUNT(telefone)                                 AS total_com_telefone,
            COUNT(email)                                    AS total_com_email,
            IFNULL(SUM(torce_flamengo), 0)                 AS torcem_flamengo,
            IFNULL(SUM(assiste_one_piece), 0)              AS assistem_one_piece,
            IFNULL(SUM(LOWER(IFNULL(cidade,''))='sousa'),0) AS de_sousa
        FROM cliente
        """
        with get_conn() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                resultado = cursor.fetchone()

                return {
                    "total_clientes":        resultado[0],
                    "clientes_com_telefone": resultado[1],
                    "clientes_com_email":    resultado[2],
                    "torcem_flamengo":       resultado[3],
                    "assistem_one_piece":    resultado[4],
                    "de_sousa":              resultado[5],
                }

            except Error as e:
                raise RuntimeError(f"Erro ao gerar relatório: {e}")

            finally:
                if cursor:
                    cursor.close()
