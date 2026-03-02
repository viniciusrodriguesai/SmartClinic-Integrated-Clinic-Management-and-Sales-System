from dotenv import load_dotenv
load_dotenv()
import os

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="smartclinic"
    )