def confirmar_pagamento(conn):
    id_usuario = input("Seu ID de usuário: ")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.ID_Pedd, pg.ID_Pag, pg.Val_Pag, pg.Form_Pag
        FROM PEDIDO p
        JOIN PAGAMENTO pg ON pg.ID_Pag = p.fk_PAGAMENTO
        WHERE p.fk_USUARIO = %s AND pg.Stat_Pag = 'Not Done'
    """, (id_usuario,))
    pedidos = cursor.fetchall()

    if not pedidos:
        print("Nenhum pagamento pendente.")
        return

    for p in pedidos:
        print(f"Pedido #{p[0]} | R${p[2]:.2f} via {p[3]}")

    ped_id = int(input("ID do pedido a confirmar: "))
    selecionado = next((p for p in pedidos if p[0] == ped_id), None)
    if not selecionado:
        print("Pedido não encontrado.")
        return

    try:
        cursor.execute("""
            UPDATE PAGAMENTO SET Stat_Pag = 'Done'
            WHERE ID_Pag = %s
        """, (selecionado[1],))
        cursor.execute("""
            UPDATE PEDIDO SET Stat_Pedd = 'pago'
            WHERE ID_Pedd = %s
        """, (ped_id,))
        conn.commit()
        print("Pagamento confirmado!")
    except Exception as e:
        conn.rollback()
        print(f"Erro: {e}")