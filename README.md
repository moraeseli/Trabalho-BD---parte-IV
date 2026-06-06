# Configuração do Banco de Dados — bd_amazon

Este guia explica como criar e conectar o banco de dados PostgreSQL usado pelo projeto, tanto via linha de comando quanto pelo pgAdmin.

---

## Pré-requisitos

- [PostgreSQL](https://www.postgresql.org/download/) instalado (versão 13 ou superior)
- [pgAdmin 4](https://www.pgadmin.org/download/) instalado (opcional, interface gráfica)
- Python 3.8+ com a biblioteca `psycopg2`:
  ```bash
  pip install psycopg2-binary
  ```

---

## 1. Criando o banco de dados

### Via linha de comando (psql)

Abra o terminal e acesse o PostgreSQL como superusuário:

```bash
psql -U postgres
```

Dentro do psql, crie o banco:

```sql
CREATE DATABASE bd_amazon;
```

Saia do psql:

```sql
\q
```

Agora execute o script SQL do projeto para criar as tabelas e inserir os dados:

```bash
psql -U postgres -d bd_amazon -f bd_amzon_100.sql
```

### Via pgAdmin 4

1. Abra o pgAdmin e conecte-se ao servidor local (`localhost`)
2. No painel à esquerda, clique com o botão direito em **Databases** → **Create** → **Database**
3. No campo **Database**, digite `bd_amazon` e clique em **Save**
4. Com o banco selecionado, clique em **Tools** → **Query Tool**
5. No editor que abrir, clique no ícone de pasta (📂) e selecione o arquivo `bd_amzon_100.sql`
6. Clique em **Execute** (▶) para rodar o script

---

## 2. Configurando a conexão no projeto

O arquivo `db.py` é responsável pela conexão com o banco:

```python
import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",   # endereço do servidor PostgreSQL
        port=5432,          # porta padrão do PostgreSQL
        dbname="bd_amazon", # nome do banco criado acima
        user="postgres",    # usuário do PostgreSQL
        password="sua_senha"# senha definida na instalação
    )
```

Substitua `"sua_senha"` pela senha que você definiu para o usuário `postgres` durante a instalação do PostgreSQL.

### Onde encontrar/redefinir a senha do postgres

**No terminal:**
```bash
psql -U postgres
```
```sql
ALTER USER postgres WITH PASSWORD 'nova_senha';
```

**No pgAdmin:**
clique com o botão direito em **Login/Group Roles** → **postgres** → **Properties** → aba **Definition** → altere a senha → **Save**

---

## 3. Verificando a conexão

Com o banco criado e `db.py` configurado, execute o sistema:

```bash
python interface.py
```

Se a conexão falhar, as mensagens de erro mais comuns são:

| Erro | Causa provável |
|---|---|
| `could not connect to server` | PostgreSQL não está rodando |
| `password authentication failed` | Senha incorreta em `db.py` |
| `database "bd_amazon" does not exist` | Banco não foi criado |
| `relation does not exist` | Script SQL não foi executado |

### Verificar se o PostgreSQL está rodando

**Windows:**
```bash
pg_ctl status -D "C:\Program Files\PostgreSQL\<versão>\data"
```

**Linux/macOS:**
```bash
sudo systemctl status postgresql  # Linux
brew services list                 # macOS com Homebrew
```

**Iniciar o serviço caso esteja parado:**
```bash
# Linux
sudo systemctl start postgresql

# macOS
brew services start postgresql

# Windows (Prompt como Administrador)
net start postgresql-x64-<versão>
```

---

## 4. Estrutura do banco

O script `bd_amzon_100.sql` cria as seguintes tabelas e já popula cada uma com 100 registros de teste:

```
LOJA          → lojas parceiras
USUARIO       → clientes cadastrados
PRODUTO       → produtos vinculados às lojas
PEDIDO        → pedidos realizados pelos usuários
PAGAMENTO     → dados de pagamento de cada pedido
ENTREGA       → informações de entrega
CUPOM         → cupons de desconto
ENDERECO      → endereços cadastrados
ASSINATURA    → planos de assinatura
CATEGORIA     → categorias de produtos
CHAT          → chats entre usuário e loja
MENSAGEM      → mensagens dentro de cada chat
AVALIACAO     → avaliações de produtos e lojas
WISHLIST      → listas de desejos dos usuários
```

Tabelas de relacionamento: `PROD_COMP_PEDD`, `PROD_PTNC_CATG`, `WL_ARMZ_PROD`, `USER_REG_ENDR`
