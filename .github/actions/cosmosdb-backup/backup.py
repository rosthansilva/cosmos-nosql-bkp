from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
from azure.mgmt.storage import StorageManagementClient
from azure.identity import DefaultAzureCredential
import json
import os
from datetime import datetime

# Configurações do Cosmos DB
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = os.getenv("DATABASE_NAME")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")

# Configurações do Azure Storage
SUBSCRIPTION_ID = os.getenv("SUBSCRIPTION_ID")
RESOURCE_GROUP = os.getenv("RESOURCE_GROUP")
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
STORAGE_CONTAINER = os.getenv("STORAGE_CONTAINER")

# Validar se todas as variáveis de ambiente necessárias estão definidas
required_env_vars = {
    "COSMOS_ENDPOINT": COSMOS_ENDPOINT,
    "COSMOS_KEY": COSMOS_KEY,
    "DATABASE_NAME": DATABASE_NAME,
    "CONTAINER_NAME": CONTAINER_NAME,
    "SUBSCRIPTION_ID": SUBSCRIPTION_ID,
    "RESOURCE_GROUP": RESOURCE_GROUP,
    "STORAGE_ACCOUNT_NAME": STORAGE_ACCOUNT_NAME,
    "STORAGE_CONTAINER": STORAGE_CONTAINER,
}

missing_vars = [key for key, value in required_env_vars.items() if not value]
if missing_vars:
    raise ValueError(f"As seguintes variáveis de ambiente estão ausentes: {', '.join(missing_vars)}")

print("Iniciando autenticação com o Azure...")
# Autenticação com o Azure usando credenciais padrão (certifique-se de estar logado no Azure CLI)
credential = DefaultAzureCredential()
storage_client = StorageManagementClient(credential, SUBSCRIPTION_ID)

print("Verificando se o Storage Account já existe...")
# Verificar se o Storage Account já existe
storage_accounts = storage_client.storage_accounts.list_by_resource_group(RESOURCE_GROUP)
account_exists = any(account.name == STORAGE_ACCOUNT_NAME for account in storage_accounts)

if not account_exists:
    print(f"Criando Storage Account: {STORAGE_ACCOUNT_NAME}")
    storage_client.storage_accounts.begin_create(
        RESOURCE_GROUP,
        STORAGE_ACCOUNT_NAME,
        {
            "location": "eastus",  # Escolha a região adequada
            "sku": {"name": "Standard_LRS"},
            "kind": "StorageV2"
        }
    ).result()
    print(f"Storage Account {STORAGE_ACCOUNT_NAME} criado com sucesso.")
else:
    print(f"Storage Account {STORAGE_ACCOUNT_NAME} já existe. Continuando com o backup...")

STORAGE_ACCOUNT_URL = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/"

print("Criando cliente do Cosmos DB...")
# Criar cliente do Cosmos DB
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

# Criar arquivo de backup
backup_filename = f"./backup_{DATABASE_NAME}_{CONTAINER_NAME}_{datetime.now().strftime('%Y-%m-%d-%H%M')}.json"

print("Iniciando exportação dos documentos do Cosmos DB...")
# Exportar os documentos do Cosmos DB para um arquivo JSON
try:
    docs = list(container.query_items(query="SELECT * FROM c", enable_cross_partition_query=True))
    print(f"{len(docs)} documentos encontrados no Cosmos DB.")
    
    with open(backup_filename, "w") as backup_file:
        json.dump(docs, backup_file, indent=4)
    
    
    print(f"Fazendo Upload para storage account usando DefaultAzureCredential: {backup_filename}")
    
    # # Criar o BlobServiceClient usando DefaultAzureCredential
    # blob_service_client = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)
    
    # # Obter o cliente do container
    # container_client = blob_service_client.get_container_client(container=STORAGE_CONTAINER)
    
    # # Fazer o upload do arquivo JSON criado
    # with open(backup_filename, "rb") as data:
    #     container_client.upload_blob(name=os.path.basename(backup_filename), data=data, overwrite=True)

    # print(f"Upload concluído com sucesso: {backup_filename}")

    print("Removendo arquivo de backup local...")
    #os.remove(backup_filename)
    print("Arquivo de backup local removido com sucesso.")
except Exception as e:
    print(f"Erro ao realizar backup: {e}")
