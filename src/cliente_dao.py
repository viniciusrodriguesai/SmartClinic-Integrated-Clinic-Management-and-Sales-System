from dataclasses import dataclass
from typing import List, Optional

from mysql.connector import Error
from db import get_conn

"""Definindo o dataclass Cliente para representar os dados de um cliente, 
com campos correspondentes às colunas da tabela cliente no banco de dados"""
@dataclass(frozen=True)
class Cliente:
    id_cliente: int
    nome: str
    cpf: str
    telefone: Optional[str]
    email: str
    data_nascimento: Optional[str]

"""Definindo a classe ClienteDAO para encapsular as operações de acesso a dados relacionadas aos clientes,
com métodos estáticos para inserir, alterar, pesquisar, remover e listar clientes, bem como um método para gerar um relatório do sistema
com base nos dados dos clientes"""
class ClienteDAO:

    @staticmethod
    def inserir(nome : str, cpf : str, telefone : Optional[str], email : str, data_nascimento : Optional[str]) -> int:
        sql = """
        INSERT INTO cliente (nome, cpf, telefone, email, data_nascimento)
        VALUES (%s, %s, %s, %s, %s)
        """
        #Abrindo conexão com o banco de dados e executando a query de inserção de um novo cliente,
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
        #Abrindo conexão com o banco de dados e executando a query de atualização do cliente
        with get_conn() as conn:
            cursor = None
            #Tratando possíveis erros durante a execução da query e garantindo o fechamento do cursor
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
            #Garantindo o fechamento do cursor mesmo em caso de erro
            finally:
                #Fechando o cursor para liberar recursos, garantindo que isso aconteça mesmo se ocorrer um erro durante a execução da query
                if cursor:
                    #Fechando o cursor para liberar recursos, garantindo que isso aconteça mesmo se ocorrer um erro durante a execução da query
                    cursor.close()

    @staticmethod
    def pesquisar_por_nome(parte_nome: str) -> List[Cliente]:

        sql = """
        SELECT id_cliente, nome, cpf, telefone, email, data_nascimento
        FROM cliente
        WHERE nome LIKE %s
        ORDER BY nome
        """
        #Abrindo conexão com o banco de dados e executando a query de pesquisa de clientes por nome, 
        # utilizando o operador LIKE para permitir buscas parciais
        with get_conn() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                #Executando a query de pesquisa de clientes por nome, utilizando o operador LIKE para permitir buscas parciais
                cursor.execute(sql, (f"%{parte_nome}%",))

                resultados = cursor.fetchall()
                #Convertendo os resultados da consulta em uma lista de objetos Cliente, 
                # utilizando a sintaxe de unpacking para passar os valores das colunas como argumentos para o construtor do dataclass Cliente
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
        #Abrindo conexão com o banco de dados e executando a query de remoção de cliente por ID,
        with get_conn() as conn:
            #Tratando possíveis erros durante a execução da query e garantindo o fechamento do cursor
            cursor = None
            #Garantindo o fechamento do cursor mesmo em caso de erro
            try:
                cursor = conn.cursor()
                #Executando a query de remoção de cliente por ID, 
                # utilizando o ID do cliente como parâmetro para identificar qual registro deve ser removido
                cursor.execute(sql, (id_cliente,))
                #Confirmando a transação para garantir que a remoção seja persistida no banco de dados
                conn.commit()
                #Retornando o número de linhas afetadas pela operação de remoção, 
                # convertendo para inteiro para garantir que o valor retornado seja do tipo esperado
                return int(cursor.rowcount)
            #
            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Erro ao remover cliente: {e}")

            finally:
                if cursor:
                    cursor.close()

    @staticmethod
    def listar_todos() -> List[Cliente]:
        #Definindo a query SQL para listar todos os clientes, ordenando por nome
        sql = """
        SELECT id_cliente, nome, cpf, telefone, email, data_nascimento
        FROM cliente
        ORDER BY nome
        """
        #Abrindo conexão com o banco de dados e executando a query de listagem de todos os clientes
        with get_conn() as conn:
            #Tratando possíveis erros durante a execução da query e garantindo o fechamento do cursor
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
                """Verificando se a consulta retornou um resultado e, em caso afirmativo, 
                criando um objeto Cliente a partir dos dados retornados,
                utilizando a sintaxe de unpacking para passar os valores das colunas 
                como argumentos para o construtor do dataclass Cliente."""
                if resultado:
                #
                    return Cliente(*resultado)

                return None

            except Error as e:
                raise RuntimeError(f"Erro ao buscar cliente: {e}")

            finally:
                if cursor:
                    cursor.close()
    #Gerar relatório do sistema, retornando um dicionário com o total de clientes, clientes com telefone e clientes com email
    @staticmethod
    def gerar_relatorio() -> dict:

        sql = """
        SELECT
            COUNT(*) AS total_clientes,
            COUNT(telefone) AS total_com_telefone,
            COUNT(email) AS total_com_email
        FROM cliente
        """

        with get_conn() as conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute(sql)

                resultado = cursor.fetchone()

                return {
                    "total_clientes": resultado[0],
                    "clientes_com_telefone": resultado[1],
                    "clientes_com_email": resultado[2],
                }

            except Error as e:
                raise RuntimeError(f"Erro ao gerar relatório: {e}")

            finally:
                if cursor:
                    cursor.close()