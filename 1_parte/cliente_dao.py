from db import conectar

class CrudManager:
    def inserir_cliente(self, nome : str, cpf : str, telefone : str, email : str, data_nascimento : str) -> int:
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

    def alterar_cliente(self, id_cliente : int, nome : str, cpf : str, telefone : str, email : str, data_nascimento : str) -> int:
        conn = conectar()
        cursor = conn.cursor()

        sql = """
        UPDATE cliente
        SET nome=%s, cpf=%s, telefone=%s, email=%s, data_nascimento=%s
        WHERE id_cliente=%s
        """
        valores = (nome, cpf, telefone, email, data_nascimento, id_cliente)

        cursor.execute(sql, valores)
        conn.commit()

        cursor.close()
        conn.close()

    def pesquisar_cliente_por_nome(self, parte_nome : str) -> list:
        conn = conectar()
        cursor = conn.cursor()

        sql = "SELECT * FROM cliente WHERE nome LIKE %s"
        valores = ("%" + parte_nome + "%",)

        cursor.execute(sql, valores)
        resultados = cursor.fetchall()

        cursor.close()
        conn.close()

        return resultados