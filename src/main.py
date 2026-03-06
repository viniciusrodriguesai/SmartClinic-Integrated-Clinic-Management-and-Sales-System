from cliente_dao import ClienteDAO


def main():
    try:
        print("=== TESTE DE INSERÇÃO ===")
        novo_id = ClienteDAO.inserir(
            nome="Ana Souza",
            cpf="123.456.789-00",
            telefone="83999999999",
            email="ana@gmail.com",
            data_nascimento="2004-10-15",
        )
        print(f"Cliente inserido com sucesso. ID: {novo_id}")

        print("\n=== TESTE DE ALTERAÇÃO ===")
        linhas_alteradas = ClienteDAO.alterar(
            id_cliente=novo_id,
            nome="Ana Silva",
            cpf="123.456.789-00",
            telefone="83988888888",
            email="ana.silva@gmail.com",
            data_nascimento="2004-10-15",
        )
        print(f"Quantidade de linhas alteradas: {linhas_alteradas}")

        print("\n=== TESTE DE PESQUISA POR NOME ===")
        clientes = ClienteDAO.pesquisar_por_nome("Ana")

        if not clientes:
            print("Nenhum cliente encontrado.")
        else:
            for cliente in clientes:
                print(cliente)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")


if __name__ == "__main__":
    main()