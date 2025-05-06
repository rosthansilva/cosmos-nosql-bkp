from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import json
import os

# Configurações do Cosmos DB
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = os.getenv("DATABASE_NAME")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")

# Configurações do Azure Storage
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
STORAGE_CONTAINER = os.getenv("STORAGE_CONTAINER")
BACKUP_FILENAME = os.getenv("BACKUP_FILENAME")  # Nome do arquivo de backup no Storage

# Validar se todas as variáveis de ambiente necessárias estão definidas
required_env_vars = {
    "COSMOS_ENDPOINT": COSMOS_ENDPOINT,
    "COSMOS_KEY": COSMOS_KEY,
    "DATABASE_NAME": DATABASE_NAME,
    "CONTAINER_NAME": CONTAINER_NAME,
    "STORAGE_ACCOUNT_NAME": STORAGE_ACCOUNT_NAME,
    "STORAGE_CONTAINER": STORAGE_CONTAINER,
    "BACKUP_FILENAME": BACKUP_FILENAME,
}

missing_vars = [key for key, value in required_env_vars.items() if not value]
if missing_vars:
    raise ValueError(f"As seguintes variáveis de ambiente estão ausentes: {', '.join(missing_vars)}")

STORAGE_ACCOUNT_URL = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/"

print("Iniciando autenticação com o Azure...")
# Autenticação com o Azure usando credenciais padrão
credential = DefaultAzureCredential()

print("Baixando arquivo de backup do Azure Storage...")
# Baixar o arquivo de backup do Azure Storage
blob_service_client = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)
blob_client = blob_service_client.get_blob_client(container=STORAGE_CONTAINER, blob=BACKUP_FILENAME)

local_backup_path = f"./{BACKUP_FILENAME}"
with open(local_backup_path, "wb") as backup_file:
    backup_file.write(blob_client.download_blob().readall())
print(f"Backup baixado com sucesso: {local_backup_path}")

print("Carregando dados do arquivo de backup...")
# Carregar os dados do arquivo de backup
with open(local_backup_path, "r") as backup_file:
    documents = json.load(backup_file)

print("Conectando ao Cosmos DB...")
# Conectar ao Cosmos DB
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

print("Iniciando restauração dos documentos no Cosmos DB...")
# Inserir os documentos no Cosmos DB
for doc in documents:
    try:
        container.upsert_item(doc)
    except Exception as e:
        print(f"Erro ao restaurar documento {doc.get('id', 'sem ID')}: {e}")

print("Restauração concluída com sucesso.")
print("Removendo arquivo de backup local...")
os.remove(local_backup_path)
print("Arquivo de backup local removido com sucesso.")