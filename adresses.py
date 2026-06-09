def registrar_endereco(conn):
    id_usuario = input("\nSeu ID de usuário: ")

    cursor = conn.cursor()

    cursor.execute("SELECT ID_User FROM USUARIO WHERE ID_User = %s", (id_usuario,))
    if not cursor.fetchone():
        print("\nUsuário não encontrado.")
        return

    print("\n--- Cadastro de Novo Endereço ---")
    cep     = input("CEP: ")
    rua     = input("Rua: ")
    numero  = input("Número: ")
    cidade  = input("Cidade: ")
    estado  = input("Estado (UF): ")
    pais    = input("País: ")

    try:
        cursor.execute("""
            INSERT INTO ENDERECO (ID_Endr, CEP_Endr, Rua_Endr, Num_Endr, Cid_Endr, Est_Endr, Pais_Endr)
            VALUES (nextval('endereco_seq'), %s, %s, %s, %s, %s, %s)
            RETURNING ID_Endr
        """, (cep, rua, numero, cidade, estado, pais))
        id_endr = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO USER_REG_ENDR (fk_ENDERECO, fk_USUARIO)
            VALUES (%s, %s)
        """, (id_endr, id_usuario))

        conn.commit()
        print(f"\nEndereço #{id_endr} cadastrado com sucesso!")
    except Exception as e:
        conn.rollback()
        print(f"\nErro ao cadastrar endereço: {e}")