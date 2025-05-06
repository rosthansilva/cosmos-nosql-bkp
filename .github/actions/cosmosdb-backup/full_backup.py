from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
from azure.mgmt.storage import StorageManagementClient
from azure.identity import DefaultAzureCredential
import json
import os
from datetime import datetime

# Cosmos DB configurations
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")

# Azure Storage configurations
SUBSCRIPTION_ID = os.getenv("SUBSCRIPTION_ID")
RESOURCE_GROUP = os.getenv("RESOURCE_GROUP")
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
STORAGE_CONTAINER = os.getenv("STORAGE_CONTAINER")

# Validate if all required environment variables are set
required_env_vars = {
    "COSMOS_ENDPOINT": COSMOS_ENDPOINT,
    "COSMOS_KEY": COSMOS_KEY,
    "SUBSCRIPTION_ID": SUBSCRIPTION_ID,
    "RESOURCE_GROUP": RESOURCE_GROUP,
    "STORAGE_ACCOUNT_NAME": STORAGE_ACCOUNT_NAME,
    "STORAGE_CONTAINER": STORAGE_CONTAINER,
}

# Extract the Cosmos DB account name from COSMOS_ENDPOINT
if COSMOS_ENDPOINT:
    cosmos_account_name = COSMOS_ENDPOINT.split("//")[1].split(".")[0]
else:
    cosmos_account_name = None

missing_vars = [key for key, value in required_env_vars.items() if not value]
if missing_vars:
    raise ValueError(f"The following environment variables are missing: {', '.join(missing_vars)}")

print("Starting authentication with Azure...")
# Authenticate with Azure using default credentials (make sure you are logged in to Azure CLI)
credential = DefaultAzureCredential()
storage_client = StorageManagementClient(credential, SUBSCRIPTION_ID)

print("Checking if the Storage Account already exists...")
# Check if the Storage Account already exists
storage_accounts = storage_client.storage_accounts.list_by_resource_group(RESOURCE_GROUP)
account_exists = any(account.name == STORAGE_ACCOUNT_NAME for account in storage_accounts)

if not account_exists:
    print(f"Creating Storage Account: {STORAGE_ACCOUNT_NAME}")
    storage_client.storage_accounts.begin_create(
        RESOURCE_GROUP,
        STORAGE_ACCOUNT_NAME,
        {
            "location": "eastus",  # Choose the appropriate region
            "sku": {"name": "Standard_LRS"},
            "kind": "StorageV2"
        }
    ).result()
    print(f"Storage Account {STORAGE_ACCOUNT_NAME} created successfully.")
else:
    print(f"Storage Account {STORAGE_ACCOUNT_NAME} already exists. Proceeding with the backup...")

STORAGE_ACCOUNT_URL = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/"

print("Creating Cosmos DB client...")
# Create Cosmos DB client
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)

print("Listing Cosmos DB databases...")
# List all databases in the Cosmos DB instance
databases = list(client.list_databases())

if not databases:
    print("No databases found in Cosmos DB.")
else:
    for database_info in databases:
        database_name = database_info['id']
        print(f"Starting backup for database: {database_name}")
        
        # Create client for the database
        database = client.get_database_client(database_name)
        
        # List all containers in the database
        containers = list(database.list_containers())
        
        if not containers:
            print(f"No containers found in database {database_name}.")
        else:
            for container_info in containers:
                container_name = container_info['id']
                print(f"Starting backup for container: {container_name}")
                
                # Create client for the container
                container = database.get_container_client(container_name)
                
                # Create directory to store the backup
                backup_dir = f"./backup/{cosmos_account_name}/{datetime.now().strftime('%Y-%m-%d-%H%M')}/{database_name}/{container_name}"
                os.makedirs(backup_dir, exist_ok=True)
                
                # Create backup file
                backup_filename = f"{backup_dir}/cosmosdb_nosql_backup_{cosmos_account_name}_{database_name}_{container_name}_{datetime.now().strftime('%Y-%m-%d-%H%M')}.json"
                
                try:
                    # Export container documents to a JSON file
                    docs = list(container.query_items(query="SELECT * FROM c", enable_cross_partition_query=True))
                    print(f"{len(docs)} documents found in container {container_name}.")

                    # Add the container name as a key in each document
                    for doc in docs:
                        doc["container_name"] = container_name

                    # Save the documents to the backup file
                    with open(backup_filename, "w") as backup_file:
                        json.dump(docs, backup_file, indent=4)
                    print(f"Backup for container {container_name} saved at: {backup_filename}")
                except Exception as e:
                    print(f"Error while backing up container {container_name}: {e}")
