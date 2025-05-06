import os
from azure.cosmos import CosmosClient

# Configurações do Cosmos DB
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")

# Validar variáveis de ambiente
if not COSMOS_ENDPOINT or not COSMOS_KEY:
    raise ValueError("As variáveis de ambiente COSMOS_ENDPOINT e COSMOS_KEY são necessárias.")

# Função para deletar todas as databases do Cosmos DB
def delete_all_databases():
    print("Iniciando processo de exclusão de todas as databases no Cosmos DB.")

    # Conectar ao Cosmos DB
    cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)

    # Listar todas as databases
    databases = list(cosmos_client.list_databases())
    if not databases:
        print("Nenhuma database encontrada para exclusão.")
        return

    print(f"{len(databases)} databases encontradas. Iniciando exclusão...")

    # Deletar cada database
    for db in databases:
        try:
            cosmos_client.delete_database(db["id"])
            print(f"Database '{db['id']}' excluída com sucesso.")
        except Exception as e:
            print(f"Erro ao excluir a database '{db['id']}': {e}")

    print("Processo de exclusão concluído.")

# Executar o script
if __name__ == "__main__":
    delete_all_databases()