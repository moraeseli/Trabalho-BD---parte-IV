def avaliar(conn):
    id_usuario = input("Seu ID de usuário: ")
    cursor = conn.cursor()

    # Valida usuário
    cursor.execute("SELECT ID_User FROM USUARIO WHERE ID_User = %s", (id_usuario,))
    if not cursor.fetchone():
        print("Usuário não encontrado.")
        return

    print("\nO que deseja avaliar?")
    print("[1] Produto")
    print("[2] Loja")
    tipo = input("Escolha: ")

    # Valida nota
    try:
        nota = int(input("Nota (1 a 5): "))
        if nota < 1 or nota > 5:
            print("Nota deve ser entre 1 e 5.")
            return
    except ValueError:
        print("Nota inválida.")
        return

    comentario = input("Comentário: ")

    try:
        if tipo == "1":
            prod_id = input("ID do produto: ")
            cursor.execute("SELECT Prod_ID FROM PRODUTO WHERE Prod_ID = %s", (prod_id,))
            if not cursor.fetchone():
                print("Produto não encontrado.")
                return
            cursor.execute("""
                INSERT INTO AVALIACAO (ID_Av, Nota_Av, Coment_Av, Ref_Av, Data_Av, fk_PRODUTO, fk_USUARIO)
                VALUES (nextval('avaliacao_seq'), %s, %s, 'Produto', CURRENT_DATE, %s, %s)
            """, (nota, comentario, prod_id, id_usuario))

        elif tipo == "2":
            loja_id = input("ID da loja: ")
            cursor.execute("SELECT ID_Loja FROM LOJA WHERE ID_Loja = %s", (loja_id,))
            if not cursor.fetchone():
                print("Loja não encontrada.")
                return
            cursor.execute("""
                INSERT INTO AVALIACAO (ID_Av, Nota_Av, Coment_Av, Ref_Av, Data_Av, fk_LOJA, fk_USUARIO)
                VALUES (nextval('avaliacao_seq'), %s, %s, 'Loja', CURRENT_DATE, %s, %s)
            """, (nota, comentario, loja_id, id_usuario))
        else:
            print("Opção inválida.")
            return

        conn.commit()
        print("Avaliação registrada!")
    except Exception as e:
        conn.rollback()
        print(f"Erro ao avaliar: {e}")

def avaliacoes_loja(conn):
    loja_id = int(input("ID da loja: "))
    while True:
        print("\n=== MINHAS AVALIAÇÕES ===")
        print("[1] Ver todas as avaliações")
        print("[2] Filtrar por nota")
        print("[0] Voltar")

        opcao = input("Escolha: ")

        if opcao == "1":
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.Nota_Av, a.Coment_Av, a.Data_Av, u.Nome_User
                FROM AVALIACAO a
                JOIN USUARIO u ON u.ID_User = a.fk_USUARIO
                WHERE a.fk_LOJA = %s
                ORDER BY a.Data_Av DESC
            """, (loja_id,))
            avaliacoes = cursor.fetchall()
            if not avaliacoes:
                print("Nenhuma avaliação encontrada.")
            for a in avaliacoes:
                print(f"Nota: {a[0]} | {a[2]} | {a[3]}: {a[1]}")

        elif opcao == "2":
            nota = int(input("Nota (1 a 5): "))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.Nota_Av, a.Coment_Av, a.Data_Av, u.Nome_User
                FROM AVALIACAO a
                JOIN USUARIO u ON u.ID_User = a.fk_USUARIO
                WHERE a.fk_LOJA = %s AND a.Nota_Av = %s
                ORDER BY a.Data_Av DESC
            """, (loja_id, nota))
            avaliacoes = cursor.fetchall()
            if not avaliacoes:
                print("Nenhuma avaliação encontrada.")
            for a in avaliacoes:
                print(f"Nota: {a[0]} | {a[2]} | {a[3]}: {a[1]}")

        elif opcao == "0":
            break
        else:
            print("Opção inválida.")