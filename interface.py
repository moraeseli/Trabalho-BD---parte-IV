from db import get_connection
from menu import menu_usuario, menu_admin, menu_loja


def main():
    try:
        conn = get_connection()
    except Exception as e:
        print(f"Falha ao conectar ao banco de dados: {e}")
        return

    perfil = input("Acesse como [1] Usuário  [2] Loja  [3] Administrador: ")

    if perfil == "1":
        menu_usuario(conn)
    elif perfil == "2":
        menu_loja(conn)
    elif perfil == "3":
        menu_admin(conn)
    else:
        print("Opção inválida.")

    conn.close()


if __name__ == "__main__":
    main()
