def analise_desempenho(conn):
    while True:
        print("\n=== ANÁLISE DE DESEMPENHO ===")
        print("[1] Faturamento total por loja")
        print("[2] Total de pedidos por loja")
        print("[3] Produtos mais vendidos")
        print("[4] Melhores lojas por avaliação")
        print("[0] Voltar")
        opcao = input("\nEscolha: ")

        if opcao == "1":
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.Nome_Loja, SUM(pg.Val_Pag) AS faturamento
                FROM PEDIDO p
                JOIN PAGAMENTO pg      ON pg.ID_Pag  = p.fk_PAGAMENTO
                JOIN PROD_COMP_PEDD pc ON pc.fk_PEDIDO = p.ID_Pedd
                JOIN PRODUTO pr        ON pr.Prod_ID  = pc.fk_PRODUTO
                JOIN LOJA l            ON l.ID_Loja   = pr.fk_LOJA
                WHERE pg.Stat_Pag = 'Done'
                GROUP BY l.Nome_Loja
                ORDER BY faturamento DESC
            """)
            print("\n=== FATURAMENTO POR LOJA ===")
            for r in cursor.fetchall():
                print(f"{r[0]} | R${r[1]:.2f}")

        elif opcao == "2":
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.Nome_Loja, COUNT(DISTINCT p.ID_Pedd) AS total_pedidos
                FROM PEDIDO p
                JOIN PROD_COMP_PEDD pc ON pc.fk_PEDIDO = p.ID_Pedd
                JOIN PRODUTO pr        ON pr.Prod_ID   = pc.fk_PRODUTO
                JOIN LOJA l            ON l.ID_Loja    = pr.fk_LOJA
                GROUP BY l.Nome_Loja
                ORDER BY total_pedidos DESC
            """)
            print("\n=== PEDIDOS POR LOJA ===")
            for r in cursor.fetchall():
                print(f"{r[0]} | {r[1]} pedido(s)")

        elif opcao == "3":
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pr.Nome_Prod, SUM(pc.Quant_Prod) AS total_vendido, l.Nome_Loja
                FROM PROD_COMP_PEDD pc
                JOIN PRODUTO pr ON pr.Prod_ID = pc.fk_PRODUTO
                JOIN LOJA l     ON l.ID_Loja  = pr.fk_LOJA
                GROUP BY pr.Nome_Prod, l.Nome_Loja
                ORDER BY total_vendido DESC
                LIMIT 10
            """)
            print("\n=== PRODUTOS MAIS VENDIDOS ===")
            for r in cursor.fetchall():
                print(f"{r[0]} | {r[1]} unidade(s) | Loja: {r[2]}")

        elif opcao == "4":
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.Nome_Loja, ROUND(AVG(a.Nota_Av)::numeric, 2) AS media,
                       COUNT(*) AS total_avaliacoes
                FROM AVALIACAO a
                JOIN LOJA l ON l.ID_Loja = a.fk_LOJA
                WHERE a.fk_LOJA IS NOT NULL
                GROUP BY l.Nome_Loja
                ORDER BY media DESC
            """)
            print("\n=== MELHORES LOJAS ===")
            for r in cursor.fetchall():
                print(f"{r[0]} | Média: {r[1]} | {r[2]} avaliação(ões)")

        elif opcao == "0":
            break
        else:
            print("\nOpção inválida.")