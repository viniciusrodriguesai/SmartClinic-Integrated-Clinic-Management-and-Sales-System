from cliente_dao import ClienteDAO


def menu():

    print("\n===== SISTEMA DE CLIENTES =====")

    print("1 - Inserir cliente")
    print("2 - Alterar cliente")
    print("3 - Pesquisar por nome")
    print("4 - Remover cliente")
    print("5 - Listar todos")
    print("6 - Exibir um cliente")
    print("0 - Sair")


def main():

    while True:

        menu()

        opcao = input("Escolha uma opção: ")

        try:

            if opcao == "1":

                nome = input("Nome: ")
                cpf = input("CPF: ")
                telefone = input("Telefone: ")
                email = input("Email: ")
                data = input("Data nascimento: ")

                id_cliente = ClienteDAO.inserir(nome, cpf, telefone, email, data)

                print("Cliente inserido com ID:", id_cliente)

            elif opcao == "2":

                id_cliente = int(input("ID do cliente: "))
                nome = input("Nome: ")
                cpf = input("CPF: ")
                telefone = input("Telefone: ")
                email = input("Email: ")
                data = input("Data nascimento: ")

                linhas = ClienteDAO.alterar(
                    id_cliente, nome, cpf, telefone, email, data
                )

                print("Clientes alterados:", linhas)

            elif opcao == "3":

                nome = input("Parte do nome: ")

                clientes = ClienteDAO.pesquisar_por_nome(nome)

                for c in clientes:
                    print(c)

            elif opcao == "4":

                id_cliente = int(input("ID do cliente: "))

                linhas = ClienteDAO.remover(id_cliente)

                print("Clientes removidos:", linhas)

            elif opcao == "5":

                clientes = ClienteDAO.listar_todos()

                for c in clientes:
                    print(c)

            elif opcao == "6":

                id_cliente = int(input("ID do cliente: "))

                cliente = ClienteDAO.buscar_por_id(id_cliente)

                print(cliente)

            elif opcao == "0":

                print("Encerrando...")
                break

        except Exception as e:

            print("Erro:", e)


if __name__ == "__main__":
    main()