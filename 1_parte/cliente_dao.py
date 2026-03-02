from db import conectar
import mysql.connector
def inserir_cliente(nome, cpf, telefone, email, data_nascimento):
    conn = conectar()
    cursor = conn.cursor()

    sql = """
    INSERT INTO cliente (nome, cpf, telefone, email, data_nascimento)
    VALUES (%s, %s, %s, %s, %s)
    """
    valores = (nome, cpf, telefone, email, data_nascimento)

    cursor.execute(sql, valores)
    conn.commit()

    cursor.close()
    conn.close()


def alterar_cliente(id_cliente, nome, cpf, telefone, email, data_nascimento):
    conn = conectar()
    cursor = conn.cursor()

    sql = """
    UPDATE cliente
    SET nome = %s,
        cpf = %s,
        telefone = %s,
        email = %s,
        data_nascimento = %s
    WHERE id_cliente = %s
    """
    valores = (nome, cpf, telefone, email, data_nascimento, id_cliente)

    cursor.execute(sql, valores)
    conn.commit()

    cursor.close()
    conn.close()


def pesquisar_cliente_por_nome(parte_nome):
    conn = conectar()
    cursor = conn.cursor()

    sql = """
    SELECT id_cliente, nome, cpf, telefone, email, data_nascimento
    FROM cliente
    WHERE nome LIKE %s
    ORDER BY nome
    """
    valores = ("%" + parte_nome + "%",)

    cursor.execute(sql, valores)
    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return resultados