import psycopg2

try:
    # Conexão com o PostgreSQL
    conexao = psycopg2.connect(
        host="localhost",
        port=5432,
        database="bdgeo",
        user="postgres",
        password="postgres"
    )

    # Criar um cursor
    cursor = conexao.cursor()

    # Executar a consulta SQL
    cursor.execute("SELECT id, nome FROM cliente ORDER BY id")

    # Recuperar todos os registros
    clientes = cursor.fetchall()

    # Exibir os resultados
    for cliente in clientes:
        print(f"ID: {cliente[0]} | Nome: {cliente[1]}")

except psycopg2.Error as erro:
    print("Erro ao acessar o PostgreSQL:", erro)

finally:
    # Encerrar a conexão
    if 'cursor' in locals():
        cursor.close()

    if 'conexao' in locals():
        conexao.close()
print ("Monica")
