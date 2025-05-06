import os
import uuid
from azure.cosmos import CosmosClient, PartitionKey

# Configurações de conexão
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = os.getenv("DATABASE_NAME")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")

# Verifica se as variáveis de ambiente estão configuradas
if not all([COSMOS_ENDPOINT, COSMOS_KEY, DATABASE_NAME, CONTAINER_NAME]):
    raise EnvironmentError("Certifique-se de que todas as variáveis de ambiente estão configuradas.")

# Inicializa o cliente do Cosmos DB
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)

# Cria o banco de dados, se não existir
database = client.create_database_if_not_exists(id=DATABASE_NAME)

# Cria o container, se não existir
container = database.create_container_if_not_exists(
    id=CONTAINER_NAME,
    partition_key=PartitionKey(path="/partitionKey"),
    offer_throughput=400
)
# Função para gerar dados falsos
def generate_fake_data():
    return {
        "id": str(uuid.uuid4()),
        "name": f"Fake Name {uuid.uuid4().hex[:8]}",
        "email": f"fake{uuid.uuid4().hex[:6]}@example.com",
        "age": 30 + (uuid.uuid4().int % 40),  # Random age between 30 and 70
        "partitionKey": "test-partition",
        "address": {
            "street": f"{uuid.uuid4().int % 1000} Fake Street",
            "city": "Faketown",
            "state": "FS",
            "zip": f"{uuid.uuid4().int % 90000 + 10000}"  # Random 5-digit zip
        },
        "phone": f"+1-{uuid.uuid4().int % 900 + 100}-{uuid.uuid4().int % 9000 + 1000}",
        "is_active": (uuid.uuid4().int % 2 == 0),  # Random boolean
        "signup_date": f"2023-{uuid.uuid4().int % 12 + 1:02d}-{uuid.uuid4().int % 28 + 1:02d}",
        "preferences": {
            "newsletter": (uuid.uuid4().int % 2 == 0),
            "notifications": (uuid.uuid4().int % 2 == 0),
            "theme": "dark" if (uuid.uuid4().int % 2 == 0) else "light"
        },
        "tags": [f"tag{uuid.uuid4().int % 10}" for _ in range(3)],  # Random tags
        "metadata": {
            "created_by": "script",
            "version": "1.0",
            "notes": "Generated for testing purposes"
        }
    }

# Insere dados falsos no container
def insert_fake_data(container, num_items=100):
    for _ in range(num_items):
        fake_data = generate_fake_data()
        container.create_item(body=fake_data)
        print(f"Inserted item with id: {fake_data['id']}")

# Insere 100 documentos falsos
if __name__ == "__main__":
    print("Inserindo dados falsos no Cosmos DB...")
    insert_fake_data(container, num_items=100)
    print("Inserção concluída.")