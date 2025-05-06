import os
import json
import argparse
from datetime import datetime
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

# Azure Storage configurations
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
STORAGE_CONTAINER = os.getenv("STORAGE_CONTAINER")
STORAGE_ACCOUNT_KEY = os.getenv("STORAGE_ACCOUNT_KEY")

# Validate environment variables
required_env_vars = {
    "STORAGE_ACCOUNT_NAME": STORAGE_ACCOUNT_NAME,
    "STORAGE_CONTAINER": STORAGE_CONTAINER,
    "STORAGE_ACCOUNT_KEY": STORAGE_ACCOUNT_KEY,
}

missing_vars = [key for key, value in required_env_vars.items() if not value]
if missing_vars:
    raise ValueError(f"The following environment variables are missing: {', '.join(missing_vars)}")

# Function to restore data to Cosmos DB
def restore_cosmos_db(restore_date, source_account, destination_account):
    print(f"Starting restore process for the destination Cosmos DB account: {destination_account} based on the backup from the account: {source_account} on date: {restore_date}")

    # Connect to Azure Blob Storage
    blob_service_client = BlobServiceClient(
        account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/",
        credential={"account_name": STORAGE_ACCOUNT_NAME, "account_key": STORAGE_ACCOUNT_KEY}
    )
    container_client = blob_service_client.get_container_client(STORAGE_CONTAINER)

    # List blobs in the container for the specified date and source account
    restore_blobs = [
        blob.name for blob in container_client.list_blobs()
        if f"{source_account}/{restore_date}" in blob.name
    ]

    if not restore_blobs:
        print(f"No backup found for date {restore_date} and account {source_account}.")
        return

    print(f"{len(restore_blobs)} backup files found. Starting restoration...")

    # Connect to the destination Cosmos DB
    COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
    COSMOS_KEY = os.getenv("COSMOS_KEY")
    if not COSMOS_ENDPOINT or not COSMOS_KEY:
        raise ValueError("The environment variables COSMOS_ENDPOINT and COSMOS_KEY are required for the restore.")

    cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)

    # Restore each backup file
    for blob_name in restore_blobs:
        print(f"Restoring blob: {blob_name}")
        blob_client = container_client.get_blob_client(blob_name)
        blob_data = blob_client.download_blob().readall()
        backup_data = json.loads(blob_data)

        # Extract information from the blob based on the directory pattern
        path_parts = blob_name.split("/")
        database_name = path_parts[-3]  # Database name
        container_name = path_parts[-2]  # Container name

        # Create database in the destination Cosmos DB
        try:
            database = cosmos_client.create_database_if_not_exists(id=database_name)
            print(f"Database {database_name} created or already exists.")
        except Exception as e:
            print(f"Error creating database {database_name}: {e}")
            continue

        # Create container in the destination Cosmos DB
        try:
            container = database.create_container_if_not_exists(
                id=container_name,
                partition_key={"paths": ["/partitionKey"], "kind": "Hash"}
            )
            print(f"Container {container_name} created or already exists.")
        except Exception as e:
            print(f"Error creating container {container_name}: {e}")
            continue

        # Insert documents into the container
        try:
            for doc in backup_data:
                container.upsert_item(doc)
            print(f"Restoration of container {container_name} completed successfully.")
        except Exception as e:
            print(f"Error restoring documents in container {container_name}: {e}")

    print("Restoration completed.")

# Configure script arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to restore Cosmos DB backups.")
    parser.add_argument("--date", required=True, help="Backup date in the format %Y-%m-%d-%H%M.")
    parser.add_argument("--source", required=True, help="Name of the source Cosmos DB account.")
    parser.add_argument("--destination", required=True, help="Name of the destination Cosmos DB account.")
    args = parser.parse_args()

    # Validate date format
    try:
        datetime.strptime(args.date, "%Y-%m-%d-%H%M")
    except ValueError:
        print("Invalid date format. Use the format %Y-%m-%d-%H%M.")
        exit(1)

    # Execute the restore process
    restore_cosmos_db(args.date, args.source, args.destination)