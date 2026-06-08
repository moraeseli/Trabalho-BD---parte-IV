def gerenciar_lojas(conn):
    # TODO: revisar - remoção de loja não verifica dependências em outras tabelas como produtos ou chats.
    while True:
        print("\n=== GERENCIAR LOJAS ===")
        print("[1] Listar lojas")
        print("[2] Cadastrar loja")
        print("[3] Remover loja")
        print("[4] Ver avaliações de uma loja")
        print("[0] Voltar")
        opcao = input("\nEscolha: ")

        if opcao == "1":
            cursor = conn.cursor()
            cursor.execute("SELECT ID_Loja, Nome_Loja, Email_Loja, Reput_Loja, Data_Criac_Loja FROM LOJA")
            print("\n--- Lista de Lojas ---")
            for l in cursor.fetchall():
                print(f"[{l[0]}] {l[1]} | {l[2]} | Reputação: {l[3]} | Desde: {l[4]}")

        elif opcao == "2":
            nome  = input("\nNome: ")
            email = input("Email: ")
            cpf_cnpj = input("CPF/CNPJ: ")
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO LOJA (Nome_Loja, Email_Loja, CPF_CNPJ_Loja, Reput_Loja, Data_Criac_Loja)
                    VALUES (%s, %s, %s, 0.0, CURRENT_DATE)
                """, (nome, email, cpf_cnpj))
                conn.commit()
                print("\nLoja cadastrada!")
            except Exception as e:
                conn.rollback()
                print(f"\nErro: {e}")

        elif opcao == "3":
            loja_id = int(input("\nID da loja: "))
            cursor = conn.cursor()
            cursor.execute("SELECT Nome_Loja FROM LOJA WHERE ID_Loja = %s", (loja_id,))
            loja = cursor.fetchone()
            if not loja:
                print("Loja não encontrada.")
                continue

            # Verifica dependências antes de tentar deletar
            cursor.execute("SELECT COUNT(*) FROM PRODUTO WHERE fk_LOJA = %s", (loja_id,))
            if cursor.fetchone()[0] > 0:
                print("Erro: esta loja possui produtos cadastrados. Remova-os primeiro.")
                continue

            cursor.execute("SELECT COUNT(*) FROM CHAT WHERE fk_LOJA = %s", (loja_id,))
            if cursor.fetchone()[0] > 0:
                print("Erro: esta loja possui chats vinculados. Encerre-os primeiro.")
                continue

            cursor.execute("SELECT COUNT(*) FROM AVALIACAO WHERE fk_LOJA = %s", (loja_id,))
            if cursor.fetchone()[0] > 0:
                print("Erro: esta loja possui avaliações registradas. Remova-as primeiro.")
                continue

            confirmacao = input(f"Confirma remoção de '{loja[0]}'? (s/n): ")
            if confirmacao.lower() != "s":
                print("Cancelado.")
                continue

            try:
                cursor.execute("DELETE FROM LOJA WHERE ID_Loja = %s", (loja_id,))
                conn.commit()
                print("Loja removida!")
            except Exception as e:
                conn.rollback()
                print(f"Erro inesperado: {e}")

        elif opcao == "4":
            loja_id = int(input("\nID da loja: "))
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
                print("\nNenhuma avaliação encontrada.")
            else:
                print("\n--- Avaliações da Loja ---")
                for a in avaliacoes:
                    print(f"Nota: {a[0]} | {a[2]} | {a[3]}: {a[1]}")

        elif opcao == "0":
            break
        else:
            print("\nOpção inválida.")