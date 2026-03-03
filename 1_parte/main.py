from cliente_dao import ClienteDAO

novo_id = ClienteDAO.inserir(
    nome="Ana Souza",
    cpf="123.456.789-00",
    telefone="83999999999",
    email="ana@gmail.com",
    data_nascimento="2004-10-15",
)
print("Inserido com id:", novo_id)

alteradas = ClienteDAO.alterar(
    id_cliente=novo_id,
    nome="Ana Silva",
    cpf="123.456.789-00",
    telefone="83988888888",
    email="ana.silva@gmail.com",
    data_nascimento="2004-10-15",
)
print("Linhas alteradas:", alteradas)

clientes = ClienteDAO.pesquisar_por_nome("Ana")
for c in clientes:
    print(c)