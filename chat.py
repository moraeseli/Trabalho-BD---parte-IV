def chat(conn):
    id_usuario = input("\nSeu ID de usuário: ")

    print("\n=== CHAT ===")
    print("[1] Iniciar novo chat")
    print("[2] Continuar chat existente")
    opcao = input("\nEscolha: ")

    cursor = conn.cursor()

    if opcao == "1":
        cursor.execute("SELECT ID_Loja, Nome_Loja FROM LOJA")
        print("\n--- Lojas ---")
        for l in cursor.fetchall():
            print(f"[{l[0]}] {l[1]}")
        loja_id = input("\nID da loja: ")

        try:
            cursor.execute("""
                INSERT INTO CHAT (ID_Chat, Stat_Chat, Open_Chat, fk_LOJA, fk_USUARIO)
                VALUES (nextval('chat_seq'), 'open', NOW(), %s, %s)
                RETURNING ID_Chat
            """, (loja_id, id_usuario))
            id_chat = cursor.fetchone()[0]
            conn.commit()
            print(f"\nChat #{id_chat} aberto!")
        except Exception as e:
            conn.rollback()
            print(f"\nErro ao abrir chat: {e}")
            return

    elif opcao == "2":
        cursor.execute("""
            SELECT ID_Chat, Stat_Chat, Open_Chat FROM CHAT
            WHERE fk_USUARIO = %s AND Stat_Chat = 'open'
        """, (id_usuario,))
        chats = cursor.fetchall()
        if not chats:
            print("\nNenhum chat aberto.")
            return
        chat_ids = [c[0] for c in chats]
        print("\n--- Chats Abertos ---")
        for c in chats:
            print(f"[{c[0]}] Status: {c[1]} | Aberto em: {c[2]}")
        
        try:
            id_chat = int(input("\nID do chat: "))
        except ValueError:
            print("\nID inválido.")
            return
        
        if id_chat not in chat_ids:
            print("\nChat inválido.")
            return

    while True:
        cursor.execute("""
            SELECT Data_hora_Msg, Conteudo_Msg,
                   CASE WHEN fk_USUARIO IS NOT NULL THEN 'Você' ELSE 'Loja' END AS remetente
            FROM MENSAGEM
            WHERE fk_CHAT = %s
            ORDER BY Data_hora_Msg
        """, (id_chat,))
        print("\n--- Mensagens ---")
        for m in cursor.fetchall():
            print(f"[{m[0]}] {m[2]}: {m[1]}")

        print("\n[1] Escrever mensagem")
        print("[0] Sair do chat")
        opcao_chat = input("\nEscolha: ")

        if opcao_chat == "0":
            break
        elif opcao_chat != "1":
            print("\nOpção inválida.")
            continue

        msg = input("\nMensagem: ")
        if not msg.strip():
            print("\nNenhuma mensagem enviada.")
            continue

        try:
            cursor.execute("""
                INSERT INTO MENSAGEM (ID_Msg, Data_hora_Msg, Conteudo_Msg, fk_USUARIO, fk_CHAT)
                VALUES (nextval('mensagem_seq'), NOW(), %s, %s, %s)
            """, (msg, id_usuario, id_chat))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"\nErro ao enviar mensagem: {e}")

def chats_loja(conn):
    loja_id = int(input("\nID da loja: "))
    while True:
        print("\n=== CHATS ===")
        print("[1] Ver chats abertos")
        print("[2] Responder chat")
        print("[3] Encerrar chat")
        print("[0] Voltar")

        opcao = input("\nEscolha: ")


        if opcao == "1":
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.ID_Chat, u.Nome_User, c.Open_Chat
                FROM CHAT c
                JOIN USUARIO u ON u.ID_User = c.fk_USUARIO
                WHERE c.fk_LOJA = %s AND c.Stat_Chat = 'open'
                ORDER BY c.Open_Chat DESC
            """, (loja_id,))
            chats = cursor.fetchall()
            if not chats:
                print("\nNenhum chat aberto.")
            else:
                print("\n--- Chats Abertos ---")
                for c in chats:
                    print(f"[{c[0]}] {c[1]} | Aberto em: {c[2]}")

        elif opcao == "2":
            chat_id = int(input("\nID do chat: "))
            cursor = conn.cursor()

            cursor.execute("""
                SELECT ID_Chat FROM CHAT WHERE ID_Chat = %s AND fk_LOJA = %s
            """, (chat_id, loja_id))
            if not cursor.fetchone():
                print("\nChat não encontrado.")
                continue

            cursor.execute("""
                SELECT Data_hora_Msg, Conteudo_Msg,
                       CASE WHEN fk_USUARIO IS NOT NULL THEN 'Cliente' ELSE 'Loja' END AS remetente
                FROM MENSAGEM
                WHERE fk_CHAT = %s
                ORDER BY Data_hora_Msg
            """, (chat_id,))
            print("\n--- Histórico ---")
            for m in cursor.fetchall():
                print(f"[{m[0]}] {m[2]}: {m[1]}")

            msg = input("\nSua resposta (Enter para cancelar): ")
            if not msg:
                continue

            try:
                cursor.execute("""
                    INSERT INTO MENSAGEM (ID_Msg, Data_hora_Msg, Conteudo_Msg, fk_LOJA, fk_CHAT)
                    VALUES (nextval('mensagem_seq'), NOW(), %s, %s, %s)
                """, (msg, loja_id, chat_id))
                conn.commit()
                print("\nMensagem enviada!")
            except Exception as e:
                conn.rollback()
                print(f"\nErro ao enviar mensagem: {e}")
                print(f"\nErro: {e}")

        elif opcao == "3":
            chat_id = int(input("\nID do chat: "))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ID_Chat FROM CHAT WHERE ID_Chat = %s AND fk_LOJA = %s
            """, (chat_id, loja_id))
            if not cursor.fetchone():
                print("\nChat não encontrado.")
                continue

            confirmacao = input("\nConfirma encerramento do chat? (s/n): ")
            if confirmacao.lower() != "s":
                print("\nCancelado.")
                continue

            try:
                cursor.execute("""
                    UPDATE CHAT SET Stat_Chat = 'closed' WHERE ID_Chat = %s
                """, (chat_id,))
                conn.commit()
                print("\nChat encerrado!")
            except Exception as e:
                conn.rollback()
                print(f"\nErro: {e}")

        elif opcao == "0":
            break
        else:
            print("\nOpção inválida.")