def fazer_pedido(conn):
    id_usuario = input("Seu ID de usuário: ")

    cursor = conn.cursor()
    cursor.execute("SELECT Prod_ID, Nome_Prod, Prec_Prod, Estoq_Prod FROM PRODUTO WHERE Estoq_Prod > 0")
    produtos = cursor.fetchall()
    for p in produtos:
        print(f"[{p[0]}] {p[1]} - R${p[2]:.2f} | Estoque: {p[3]}")

    prod_id = input("ID do produto: ")
    quantidade = input("Quantidade: ")

    cursor.execute("SELECT Estoq_Prod, Prec_Prod FROM PRODUTO WHERE Prod_ID = %s", (prod_id,))
    produto = cursor.fetchone()
    if not produto or int(quantidade) > produto[0]:
        print("Estoque insuficiente.")
        return

    cursor.execute("""
        SELECT e.ID_Endr, e.Rua_Endr, e.Num_Endr, e.Cid_Endr, e.Est_Endr, e.Pais_Endr, e.CEP_Endr
        FROM ENDERECO e
        JOIN USER_REG_ENDR ur ON ur.fk_ENDERECO = e.ID_Endr
        WHERE ur.fk_USUARIO = %s
    """, (id_usuario,))
    enderecos = cursor.fetchall()

    if not enderecos:
        print("Nenhum endereço cadastrado. Cadastre um endereço antes de fazer um pedido.")
        return

    print("\nEndereços cadastrados:")
    for e in enderecos:
        print(f"[{e[0]}] {e[1]}, {e[2]} - {e[3]}/{e[4]} - {e[5]} - CEP {e[6]}")

    endereco_id = input("ID do endereço de entrega: ")
    if not any(str(e[0]) == endereco_id for e in enderecos):
        print("Endereço inválido.")
        return

    print("\nForma de pagamento:")
    print("[1] Pix")
    print("[2] Crédito")
    print("[3] Débito")
    print("[4] Boleto")
    formas = {"1": "Pix", "2": "Crédito", "3": "Débito", "4": "Boleto"}
    forma = formas.get(input("Escolha: "), "Pix")
    valor = produto[1] * int(quantidade)

    cursor.execute("""
        SELECT ID_Cupom, Val_Min_Cupom, Val_Cupom, Tipo_Cupom
        FROM CUPOM
        WHERE Val_Min_Cupom <= %s
    """, (valor,))
    cupons = cursor.fetchall()

    cupom_id = None
    desconto = 0.0
    valor_final = valor

    if cupons:
        print("\nCupons disponíveis:")
        for c in cupons:
            print(f"[{c[0]}] Mínimo R${c[1]:.2f} - {c[3]} {c[2]}{'%' if c[3] == 'Porcent' else ''}")

        usar_cupom = input("Deseja usar um cupom? [s/N]: ").strip().lower()
        if usar_cupom == 's':
            cupom_id = input("ID do cupom: ")
            selected = next((c for c in cupons if str(c[0]) == cupom_id), None)
            if selected:
                if selected[3] == 'Fixo':
                    desconto = float(selected[2])
                elif selected[3] == 'Porcent':
                    desconto = valor * float(selected[2])
                else:
                    desconto = 0.0

                desconto = min(desconto, valor)
                valor_final = valor - desconto
                print(f"Desconto aplicado: R${desconto:.2f}. Total final: R${valor_final:.2f}")
            else:
                print("Cupom inválido. Nenhum desconto será aplicado.")
                cupom_id = None
    else:
        print("\nNenhum cupom disponível para esse valor de pedido.")

    try:
        cursor.execute("""
            INSERT INTO PAGAMENTO (ID_Pag, Form_Pag, Val_Pag, Stat_Pag)
            VALUES (nextval('pagamento_seq'), %s, %s, 'Not Done')
            RETURNING ID_Pag
        """, (forma, valor_final))
        id_pag = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO PEDIDO (ID_Pedd, Stat_Pedd, timestamp_Pedd, fk_PAGAMENTO, fk_USUARIO, fk_ENDERECO, fk_CUPOM)
            VALUES (nextval('pedido_seq'), 'em processamento', NOW(), %s, %s, %s, %s)
            RETURNING ID_Pedd
        """, (id_pag, id_usuario, endereco_id, cupom_id))
        id_pedd = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO PROD_COMP_PEDD (Quant_Prod, fk_PEDIDO, fk_PRODUTO)
            VALUES (%s, %s, %s)
        """, (quantidade, id_pedd, prod_id))

        cursor.execute("""
            UPDATE PRODUTO SET Estoq_Prod = Estoq_Prod - %s WHERE Prod_ID = %s
        """, (quantidade, prod_id))

        conn.commit()
        print(f"\nPedido #{id_pedd} criado! Total: R${valor_final:.2f}")
    except Exception as e:
        conn.rollback()
        print(f"Erro ao criar pedido: {e}")

def verificar_pedidos(conn):
    while True:
        print("[1] Listar todos os pedidos")
        print("[2] Filtrar por status")
        print("[3] Atualizar status de um pedido")
        print("[0] Voltar")

        opcao = input("Escolha: ")

        if opcao == "1":
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.ID_Pedd, u.Nome_User, pg.Val_Pag, pg.Form_Pag,
                       p.Stat_Pedd, p.timestamp_Pedd
                FROM PEDIDO p
                JOIN USUARIO u    ON u.ID_User  = p.fk_USUARIO
                JOIN PAGAMENTO pg ON pg.ID_Pag  = p.fk_PAGAMENTO
                ORDER BY p.timestamp_Pedd DESC
            """)
            for p in cursor.fetchall():
                print(f"[{p[0]}] {p[1]} | R${p[2]:.2f} {p[3]} | {p[4]} | {p[5]}")

        elif opcao == "2":
            print("\nStatus disponíveis: em processamento, pago, enviado, entregue, cancelado")
            status = input("Status: ")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.ID_Pedd, u.Nome_User, pg.Val_Pag, p.Stat_Pedd, p.timestamp_Pedd
                FROM PEDIDO p
                JOIN USUARIO u    ON u.ID_User = p.fk_USUARIO
                JOIN PAGAMENTO pg ON pg.ID_Pag = p.fk_PAGAMENTO
                WHERE p.Stat_Pedd = %s
                ORDER BY p.timestamp_Pedd DESC
            """, (status,))
            pedidos = cursor.fetchall()
            if not pedidos:
                print("Nenhum pedido encontrado.")
            for p in pedidos:
                print(f"[{p[0]}] {p[1]} | R${p[2]:.2f} | {p[3]} | {p[4]}")

        elif opcao == "3":
            ped_id = int(input("ID do pedido: "))
            cursor = conn.cursor()
            cursor.execute("SELECT Stat_Pedd FROM PEDIDO WHERE ID_Pedd = %s", (ped_id,))
            pedido = cursor.fetchone()
            if not pedido:
                print("Pedido não encontrado.")
                continue

            print(f"Status atual: {pedido[0]}")
            print("Novo status: em processamento / pago / enviado / entregue / cancelado")
            novo_status = input("Status: ")

            try:
                cursor.execute("""
                    UPDATE PEDIDO SET Stat_Pedd = %s WHERE ID_Pedd = %s
                """, (novo_status, ped_id))
                conn.commit()
                print("Status atualizado!")
            except Exception as e:
                conn.rollback()
                print(f"Erro: {e}")

        elif opcao == "0":
            break
        else:
            print("Opção inválida.")

def pedidos_loja(conn):
    loja_id = int(input("ID da loja: "))
    while True:
        print("[1] Ver todos os meus pedidos")
        print("[2] Filtrar por status")
        print("[3] Atualizar status de um pedido")
        print("[0] Voltar")

        opcao = input("Escolha: ")

        if opcao == "1":
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT p.ID_Pedd, u.Nome_User, pg.Val_Pag,
                       pg.Form_Pag, p.Stat_Pedd, p.timestamp_Pedd
                FROM PEDIDO p
                JOIN USUARIO u         ON u.ID_User   = p.fk_USUARIO
                JOIN PAGAMENTO pg      ON pg.ID_Pag   = p.fk_PAGAMENTO
                JOIN PROD_COMP_PEDD pc ON pc.fk_PEDIDO = p.ID_Pedd
                JOIN PRODUTO pr        ON pr.Prod_ID   = pc.fk_PRODUTO
                WHERE pr.fk_LOJA = %s
                ORDER BY p.timestamp_Pedd DESC
            """, (loja_id,))
            pedidos = cursor.fetchall()
            if not pedidos:
                print("Nenhum pedido encontrado.")
            for p in pedidos:
                print(f"[{p[0]}] {p[1]} | R${p[2]:.2f} {p[3]} | {p[4]} | {p[5]}")

        elif opcao == "2":
            status = input("Status (em processamento/pago/enviado/entregue/cancelado): ")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT p.ID_Pedd, u.Nome_User, pg.Val_Pag, p.Stat_Pedd, p.timestamp_Pedd
                FROM PEDIDO p
                JOIN USUARIO u         ON u.ID_User    = p.fk_USUARIO
                JOIN PAGAMENTO pg      ON pg.ID_Pag    = p.fk_PAGAMENTO
                JOIN PROD_COMP_PEDD pc ON pc.fk_PEDIDO = p.ID_Pedd
                JOIN PRODUTO pr        ON pr.Prod_ID   = pc.fk_PRODUTO
                WHERE pr.fk_LOJA = %s AND p.Stat_Pedd = %s
                ORDER BY p.timestamp_Pedd DESC
            """, (loja_id, status))
            pedidos = cursor.fetchall()
            if not pedidos:
                print("Nenhum pedido encontrado.")
            for p in pedidos:
                print(f"[{p[0]}] {p[1]} | R${p[2]:.2f} | {p[3]} | {p[4]}")

        elif opcao == "3":
            ped_id = int(input("ID do pedido: "))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.Stat_Pedd FROM PEDIDO p
                JOIN PROD_COMP_PEDD pc ON pc.fk_PEDIDO = p.ID_Pedd
                JOIN PRODUTO pr        ON pr.Prod_ID   = pc.fk_PRODUTO
                WHERE p.ID_Pedd = %s AND pr.fk_LOJA = %s
            """, (ped_id, loja_id))
            pedido = cursor.fetchone()
            if not pedido:
                print("Pedido não encontrado.")
                continue

            print(f"Status atual: {pedido[0]}")
            novo_status = input("Novo status (em processamento/pago/enviado/entregue/cancelado): ")

            try:
                cursor.execute("""
                    UPDATE PEDIDO SET Stat_Pedd = %s WHERE ID_Pedd = %s
                """, (novo_status, ped_id))
                conn.commit()
                print("Status atualizado!")
            except Exception as e:
                conn.rollback()
                print(f"Erro: {e}")

        elif opcao == "0":
            break
        else:
            print("Opção inválida.")