def ver_produtos(conn):
    while True:
        print("\n=== VER PRODUTOS ===")
        print("[1] Listar todos")
        print("[2] Filtrar por categoria")
        print("[3] Filtrar por preço")
        print("[4] Buscar por nome")
        print("[5] Ver detalhes de um produto")
        print("[0] Voltar")
        opcao = input("\nEscolha: ")

        if opcao == "1":
            cursor = conn.cursor()
            cursor.execute("SELECT Prod_ID, Nome_Prod, Prec_Prod, Marca_Prod, Estoq_Prod FROM PRODUTO")
            print("\n--- Listagem de Produtos ---")
            for p in cursor.fetchall():
                print(f"[{p[0]}] {p[1]} - R${p[2]:.2f} | Marca: {p[3]} | Estoque: {p[4]}")

        elif opcao == "2":
            cursor = conn.cursor()
            cursor.execute("SELECT ID_Catg, Nome_Catg FROM CATEGORIA")
            print("\n--- Categorias ---")
            for c in cursor.fetchall():
                print(f"[{c[0]}] {c[1]}")
            cat = input("\nID da categoria: ")
            cursor.execute("""
                SELECT p.Prod_ID, p.Nome_Prod, p.Prec_Prod, p.Marca_Prod
                FROM PRODUTO p
                JOIN PROD_PTNC_CATG pc ON pc.fk_PRODUTO = p.Prod_ID
                WHERE pc.fk_CATEGORIA = %s
            """, (cat,))
            print("\n--- Produtos da Categoria ---")
            for p in cursor.fetchall():
                print(f"[{p[0]}] {p[1]} - R${p[2]:.2f} | Marca: {p[3]}")

        elif opcao == "3":
            minimo = input("\nPreço mínimo (Enter para 0): ") or "0"
            maximo = input("Preço máximo (Enter para sem limite): ") or "999999"
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Prod_ID, Nome_Prod, Prec_Prod, Marca_Prod
                FROM PRODUTO
                WHERE Prec_Prod BETWEEN %s AND %s
                ORDER BY Prec_Prod
            """, (minimo, maximo))
            print("\n--- Produtos no Preço Selecionado ---")
            for p in cursor.fetchall():
                print(f"[{p[0]}] {p[1]} - R${p[2]:.2f} | Marca: {p[3]}")

        elif opcao == "4":
            nome = input("\nNome do produto: ")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Prod_ID, Nome_Prod, Prec_Prod, Marca_Prod
                FROM PRODUTO
                WHERE Nome_Prod ILIKE %s
            """, (f"%{nome}%",))
            print("\n--- Resultados da Busca ---")
            for p in cursor.fetchall():
                print(f"[{p[0]}] {p[1]} - R${p[2]:.2f} | Marca: {p[3]}")

        elif opcao == "5":
            prod_id = input("\nID do produto: ")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.Nome_Prod, p.Prec_Prod, p.Desc_Prod, p.Marca_Prod,
                       p.Model_Prod, p.Estoq_Prod, l.Nome_Loja
                FROM PRODUTO p
                JOIN LOJA l ON l.ID_Loja = p.fk_LOJA
                WHERE p.Prod_ID = %s
            """, (prod_id,))
            p = cursor.fetchone()
            if p:
                print(f"\n--- Detalhes do Produto ---")
                print(f"Nome:     {p[0]}")
                print(f"Preço:    R${p[1]:.2f}")
                print(f"Descrição: {p[2]}")
                print(f"Marca:    {p[3]}")
                print(f"Modelo:   {p[4]}")
                print(f"Estoque:  {p[5]}")
                print(f"Loja:     {p[6]}")
            else:
                print("\nProduto não encontrado.")

        elif opcao == "0":
            break
        else:
            print("\nOpção inválida.")

def gerenciar_produtos(conn):
    while True:
        print("\n=== GERENCIAR PRODUTOS ===")
        print("[1] Cadastrar produto")
        print("[2] Editar produto")
        print("[3] Remover produto")
        print("[0] Voltar")
        opcao = input("\nEscolha: ")

        if opcao == "1":
                nome      = input("Nome: ")
                preco     = float(input("Preço: "))
                descricao = input("Descrição: ")
                marca     = input("Marca: ")
                modelo    = input("Modelo: ")
                estoque   = int(input("Estoque: "))
                tipo      = input("Tipo (físico/digital): ").lower()

                cursor = conn.cursor()
                cursor.execute("SELECT ID_Loja, Nome_Loja FROM LOJA")
                for l in cursor.fetchall():
                    print(f"[{l[0]}] {l[1]}")
                loja_id = int(input("ID da loja: "))

                try:
                    cursor.execute("""
                        INSERT INTO PRODUTO (Nome_Prod, Prec_Prod, Desc_Prod, Marca_Prod,
                                            Model_Prod, Estoq_Prod, Tipo_Prod, fk_LOJA)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (nome, preco, descricao, marca, modelo, estoque, tipo, loja_id))
                    conn.commit()
                    print("Produto cadastrado!")
                except Exception as e:
                    conn.rollback()
                    print(f"Erro ao cadastrar produto: {e}")

        elif opcao == "2":
            cursor = conn.cursor()

            prod_id = int(input("ID do produto: "))
            cursor.execute("SELECT * FROM PRODUTO WHERE Prod_ID = %s", (prod_id,))
            produto = cursor.fetchone()
            if not produto:
                print("Produto não encontrado.")
                continue

            print("Deixe em branco para manter o valor atual.")
            nome      = input(f"Nome [{produto[1]}]: ")      or produto[1]
            preco     = input(f"Preço [{produto[2]}]: ")     or produto[2]
            descricao = input(f"Descrição [{produto[3]}]: ") or produto[3]
            marca     = input(f"Marca [{produto[4]}]: ")     or produto[4]
            modelo    = input(f"Modelo [{produto[5]}]: ")    or produto[5]
            estoque   = input(f"Estoque [{produto[6]}]: ")   or produto[6]
            tipo      = input(f"Tipo [{produto[7]}]: ")      or produto[7]

            try:
                cursor.execute("""
                    UPDATE PRODUTO
                    SET Nome_Prod=%s, Prec_Prod=%s, Desc_Prod=%s, Marca_Prod=%s,
                        Model_Prod=%s, Estoq_Prod=%s, Tipo_Prod=%s
                    WHERE Prod_ID=%s
                """, (nome, preco, descricao, marca, modelo, estoque, tipo, prod_id))
                conn.commit()
                print("Produto atualizado!")
            except Exception as e:
                conn.rollback()
                print(f"Erro: {e}")

        elif opcao == "3":
            cursor = conn.cursor()

            prod_id = int(input("ID do produto: "))
            cursor.execute("SELECT Nome_Prod FROM PRODUTO WHERE Prod_ID = %s", (prod_id,))
            produto = cursor.fetchone()
            if not produto:
                print("Produto não encontrado.")
                return

            confirmacao = input(f"Confirma remoção de '{produto[0]}'? (s/n): ")
            if confirmacao.lower() != "s":
                print("Cancelado.")
                return

            try:
                cursor.execute("DELETE FROM PRODUTO WHERE Prod_ID = %s", (prod_id,))
                conn.commit()
                print("Produto removido!")
            except Exception as e:
                conn.rollback()
                print(f"Erro: {e}")

        elif opcao == "0":
            break
        else:
            print("Opção inválida.")

def gerenciar_produtos_loja(conn):
    loja_id = int(input("ID da loja: "))
    while True:
        print("\n=== GERENCIAR MEUS PRODUTOS ===")
        print("[1] Listar meus produtos")
        print("[2] Cadastrar produto")
        print("[3] Editar produto")
        print("[4] Remover produto")
        print("[0] Voltar")

        opcao = input("Escolha: ")

        if opcao == "1":
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Prod_ID, Nome_Prod, Prec_Prod, Estoq_Prod
                FROM PRODUTO
                WHERE fk_LOJA = %s
            """, (loja_id,))
            produtos = cursor.fetchall()
            if not produtos:
                print("Nenhum produto encontrado.")
            for p in produtos:
                print(f"[{p[0]}] {p[1]} | R${p[2]:.2f} | Estoque: {p[3]}")

        elif opcao == "2":
            nome      = input("Nome: ")
            preco     = float(input("Preço: "))
            descricao = input("Descrição: ")
            marca     = input("Marca: ")
            modelo    = input("Modelo: ")
            estoque   = int(input("Estoque: "))
            tipo      = input("Tipo (físico/digital): ")
            try:
                cursor = conn.cursor()
                cursor.execute("""
                        INSERT INTO PRODUTO (Prod_ID, Nome_Prod, Prec_Prod, Desc_Prod, Marca_Prod,
                        Model_Prod, Estoq_Prod, Tipo_Prod, fk_LOJA)
                        VALUES (nextval('produto_seq'), %s, %s, %s, %s, %s, %s, %s, %s)
                """, (nome, preco, descricao, marca, modelo, estoque, tipo, loja_id))
                conn.commit()
                print("Produto cadastrado!")
            except Exception as e:
                conn.rollback()
                print(f"Erro: {e}")

        elif opcao == "3":
            prod_id = int(input("ID do produto: "))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM PRODUTO WHERE Prod_ID = %s AND fk_LOJA = %s
            """, (prod_id, loja_id))
            p = cursor.fetchone()
            if not p:
                print("Produto não encontrado.")
                continue

            print("Deixe em branco para manter o valor atual.")
            nome      = input(f"Nome [{p[1]}]: ")      or p[1]
            preco     = input(f"Preço [{p[2]}]: ")     or p[2]
            descricao = input(f"Descrição [{p[3]}]: ") or p[3]
            marca     = input(f"Marca [{p[4]}]: ")     or p[4]
            modelo    = input(f"Modelo [{p[5]}]: ")    or p[5]
            estoque   = input(f"Estoque [{p[6]}]: ")   or p[6]
            tipo      = input(f"Tipo [{p[7]}]: ")      or p[7]

            try:
                cursor.execute("""
                    UPDATE PRODUTO
                    SET Nome_Prod=%s, Prec_Prod=%s, Desc_Prod=%s, Marca_Prod=%s,
                        Model_Prod=%s, Estoq_Prod=%s, Tipo_Prod=%s
                    WHERE Prod_ID=%s AND fk_LOJA=%s
                """, (nome, preco, descricao, marca, modelo, estoque, tipo, prod_id, loja_id))
                conn.commit()
                print("Produto atualizado!")
            except Exception as e:
                conn.rollback()
                print(f"Erro: {e}")

        elif opcao == "4":
            prod_id = int(input("ID do produto: "))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Nome_Prod FROM PRODUTO WHERE Prod_ID = %s AND fk_LOJA = %s
            """, (prod_id, loja_id))
            p = cursor.fetchone()
            if not p:
                print("Produto não encontrado.")
                continue

            confirmacao = input(f"Confirma remoção de '{p[0]}'? (s/n): ")
            if confirmacao.lower() != "s":
                print("Cancelado.")
                continue

            try:
                cursor.execute("DELETE FROM PRODUTO WHERE Prod_ID = %s AND fk_LOJA = %s", (prod_id, loja_id))
                conn.commit()
                print("Produto removido!")
            except Exception as e:
                conn.rollback()
                print(f"Erro: {e}")

        elif opcao == "0":
            break
        else:
            print("Opção inválida.")