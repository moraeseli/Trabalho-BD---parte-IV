def gerenciar_assinaturas(conn):
    while True:
        print("\n=== GERENCIAR ASSINATURAS ===")
        print("[1] Listar assinaturas")
        print("[2] Criar assinatura")
        print("[3] Editar assinatura")
        print("[4] Remover assinatura")
        print("[5] Ver usuários de uma assinatura")
        print("[0] Voltar")

        opcao = input("Escolha: ")

        if opcao == "1":
            cursor = conn.cursor()
            cursor.execute("SELECT ID_Ass, Nome_Ass, Prec_Ass, Free_Frete FROM ASSINATURA")
            for a in cursor.fetchall():
                frete = "Sim" if a[3] else "Não"
                print(f"[{a[0]}] {a[1]} | R${a[2]:.2f} | Frete grátis: {frete}")

        elif opcao == "2":
            nome   = input("Nome: ")
            preco  = float(input("Preço: "))
            frete  = input("Frete grátis? (s/n): ").lower() == "s"
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ASSINATURA (Nome_Ass, Prec_Ass, Free_Frete)
                    VALUES (%s, %s, %s)
                """, (nome, preco, frete))
                conn.commit()
                print("Assinatura criada!")
            except Exception as e:
                conn.rollback()
                print(f"Erro: {e}")

        elif opcao == "3":
            ass_id = int(input("ID da assinatura: "))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ASSINATURA WHERE ID_Ass = %s", (ass_id,))
            a = cursor.fetchone()
            if not a:
                print("Assinatura não encontrada.")
                continue

            print("Deixe em branco para manter o valor atual.")
            nome  = input(f"Nome [{a[1]}]: ")  or a[1]
            preco = input(f"Preço [{a[2]}]: ") or a[2]
            frete = input(f"Frete grátis [{a[3]}] (s/n): ")
            frete = a[3] if frete == "" else frete.lower() == "s"

            try:
                cursor.execute("""
                    UPDATE ASSINATURA SET Nome_Ass=%s, Prec_Ass=%s, Free_Frete=%s
                    WHERE ID_Ass=%s
                """, (nome, preco, frete, ass_id))
                conn.commit()
                print("Assinatura atualizada!")
            except Exception as e:
                conn.rollback()
                print(f"Erro: {e}")

        elif opcao == "4":
            ass_id = int(input("ID da assinatura: "))
            cursor = conn.cursor()
            cursor.execute("SELECT Nome_Ass FROM ASSINATURA WHERE ID_Ass = %s", (ass_id,))
            a = cursor.fetchone()
            if not a:
                print("Assinatura não encontrada.")
                continue

            confirmacao = input(f"Confirma remoção de '{a[0]}'? (s/n): ")
            if confirmacao.lower() != "s":
                print("Cancelado.")
                continue

            try:
                cursor.execute("DELETE FROM ASSINATURA WHERE ID_Ass = %s", (ass_id,))
                conn.commit()
                print("Assinatura removida!")
            except Exception as e:
                conn.rollback()
                print(f"Erro: {e}")

        elif opcao == "5":
            ass_id = int(input("ID da assinatura: "))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.ID_User, u.Nome_User, u.Email_User
                FROM USUARIO u
                WHERE u.fk_ASSINATURA = %s
            """, (ass_id,))
            usuarios = cursor.fetchall()
            if not usuarios:
                print("Nenhum usuário com essa assinatura.")
            for u in usuarios:
                print(f"[{u[0]}] {u[1]} | {u[2]}")

        elif opcao == "0":
            break
        else:
            print("Opção inválida.")