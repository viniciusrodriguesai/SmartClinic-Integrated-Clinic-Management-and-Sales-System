import mysql.connector

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="SEU_USUARIO",
        password="SUA_SENHA",
        database="smartclinic"
    )