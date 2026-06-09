from products import ver_produtos, gerenciar_produtos, gerenciar_produtos_loja
from stores import gerenciar_lojas
from orders import fazer_pedido, verificar_pedidos, pedidos_loja
from subscriptions import gerenciar_assinaturas
from analytics import analise_desempenho
from reviews import avaliar, avaliacoes_loja
from chat import chat, chats_loja
from payments import confirmar_pagamento
from adresses import registrar_endereco

def menu_usuario(conn):
    while True:
        print("\n=== MENU USUÁRIO ===")
        print("[1] Ver produtos")
        print("[2] Fazer pedido")
        print("[3] Avaliar produto ou loja")
        print("[4] Chat com a loja")
        print("[5] Confirmar pagamento")
        print("[6] Registrar novo endereço")
        print("[0] Sair")
        opcao = input("\nEscolha: ")

        if opcao == "1":
            ver_produtos(conn)
        elif opcao == "2":
            fazer_pedido(conn)
        elif opcao == "3":
            avaliar(conn)
        elif opcao == "4":
            chat(conn)
        elif opcao == "5":
            confirmar_pagamento(conn)
        elif opcao == "6":
            registrar_endereco(conn)
        elif opcao == "0":
            break
        else:
            print("\nOpção inválida.")


def menu_admin(conn):
    while True:
        print("\n=== MENU ADMINISTRADOR ===")
        print("[1] Gerenciar lojas")
        print("[2] Gerenciar produtos")
        print("[3] Verificar pedidos")
        print("[4] Gerenciar assinaturas")
        print("[5] Análise de desempenho")
        print("[0] Sair")
        opcao = input("\nEscolha: ")

        if opcao == "1":
            gerenciar_lojas(conn)
        elif opcao == "2":
            gerenciar_produtos(conn)
        elif opcao == "3":
            verificar_pedidos(conn)
        elif opcao == "4":
            gerenciar_assinaturas(conn)
        elif opcao == "5":
            analise_desempenho(conn)
        elif opcao == "0":
            break
        else:
            print("\nOpção inválida.")


def menu_loja(conn):
    while True:
        print("\n=== MENU LOJA ===")
        print("[1] Gerenciar meus produtos")
        print("[2] Acompanhar pedidos")
        print("[3] Responder chats")
        print("[4] Ver minhas avaliações")
        print("[0] Sair")
        opcao = input("\nEscolha: ")

        if opcao == "1":
            gerenciar_produtos_loja(conn)
        elif opcao == "2":
            pedidos_loja(conn)
        elif opcao == "3":
            chats_loja(conn)
        elif opcao == "4":
            avaliacoes_loja(conn)
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")