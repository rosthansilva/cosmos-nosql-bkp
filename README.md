# Backup CosmosDB GitHub Action

![CosmosDB Backup](https://markpatton.cloud/wp-content/uploads/2020/03/definingbackuppolicycosmosdb-img-e1585163856238.png)

This GitHub Action automates the process of backing up a CosmosDB database to Azure Storage. It is designed to run on a schedule or be triggered manually via the `workflow_dispatch` event.

## Workflow Example Overview

- **Name**: Backup CosmosDB
- **Triggers**:
    - Scheduled as a cron job.
    - Can also be triggered manually.
    - Runs on the `main` branch upon push events.

## Job Details

### Job: `backup`
- **Environment**: `ubuntu-latest`
- **Steps**:
    1. **Checkout Repository**: Uses the `actions/checkout@v4` action to clone the repository.
    2. **Backup CosmosDB**: Executes a custom GitHub Action located at `.github/actions/cosmosdb-backup` to perform the backup operation.

## Inputs for Backup Action

The following inputs are required for the backup action:

- **Azure Credentials**:
    - `AZURE_CREDENTIALS`: Azure credentials stored as a GitHub secret.
    - `ARM_CLIENT_ID`: Azure Resource Manager client ID.
    - `ARM_CLIENT_SECRET`: Azure Resource Manager client secret.
    - `ARM_SUBSCRIPTION_ID`: Azure subscription ID.
    - `ARM_TENANT_ID`: Azure tenant ID.

- **CosmosDB Configuration**:
    - `COSMOS_ENDPOINT`: The endpoint URL of the CosmosDB account.
    - `COSMOS_KEY`: The primary key for the CosmosDB account.
    - `DATABASE_NAME`: The name of the CosmosDB database to back up.
    - `CONTAINER_NAME`: The name of the CosmosDB container to back up.

- **Azure Storage Configuration**:
    - `STORAGE_ACCOUNT_NAME`: The name of the Azure Storage account where the backup will be stored.
    - `STORAGE_CONTAINER`: The name of the Azure Storage container for the backup.

- **Resource Group**:
    - `RESOURCE_GROUP`: The name of the Azure resource group containing the CosmosDB account.

- **Action**:
    - `action`: Specifies the operation to perform. In this case, it is set to `"backup"`.
    - **Restore Action**: The restore functionality is not yet implemented. This feature is planned for future development to allow restoring data from Azure Storage back to a CosmosDB database.

## Usage

To use this workflow, ensure that all required secrets are configured in your GitHub repository settings. The workflow will automatically back up the specified CosmosDB database to the designated Azure Storage container.

## Example Workflow File

Below is an example of a GitHub Actions workflow file to back up a CosmosDB database:

```yaml
name: Backup CosmosDB

on:
    workflow_dispatch:
    schedule:
        - cron: "0 2 * * *" # Every day at 2 AM UTC
    push:
        branches:
            - main

jobs:
    backup:
        runs-on: ubuntu-latest

        steps:
            - name: Checkout repo
                uses: actions/checkout@v4

            - name: Backup CosmosDB to Azure Storage
                uses: ./.github/actions/cosmosdb-backup
                with:
                    AZURE_CREDENTIALS: ${{ secrets.AZURE_CREDENTIALS }}
                    ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
                    ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
                    ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}
                    ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}
                    COSMOS_ENDPOINT: "https://cosmos-cosmosdb-account.documents.azure.com:443" #$${{ secrets.COSMOS_ENDPOINT }}
                    COSMOS_KEY: ${{ secrets.COSMOS_KEY }}
                    CONTAINER_NAME: "cosmos-container-src"
                    DATABASE_NAME: "cosmos-database"
                    RESOURCE_GROUP: "cosmos-resources"
                    STORAGE_ACCOUNT_NAME: "cosmosbkp1123"
                    STORAGE_CONTAINER: "cosmos-backup-container"
                    SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
                    action: "backup" # "full_backup" to backup all databases and containers.
```

## Github Restore Script in Composite Actions

## Overview
This workflow is designed to restore data from Azure Storage to an Azure CosmosDB instance. It utilizes a custom composite action to securely interact with Azure resources and perform the restore operation.

## Key Features
- **Restore Trigger**: The workflow can be triggered manually via `workflow_dispatch` or on pushes to the `main` branch.
- **Custom Composite Action**: The `.github/actions/cosmosdb-backup` action is used to handle the restore logic. Ensure this action is implemented and available in the repository.
- **Secure Credentials**: Azure credentials and CosmosDB keys are securely stored as GitHub secrets and passed to the workflow.

## Steps
### Restore Job
1. **Checkout Repository**: Uses the `actions/checkout@v4` action to clone the repository.
2. **Restore CosmosDB**: Executes the custom composite action to restore the specified CosmosDB database and container from Azure Storage.

## Configuration
- **Azure Credentials**: Ensure the following secrets are configured in the repository:
    - `AZURE_CREDENTIALS`
    - `ARM_CLIENT_ID`
    - `ARM_CLIENT_SECRET`
    - `ARM_SUBSCRIPTION_ID`
    - `ARM_TENANT_ID`
    - `COSMOS_KEY`
- **CosmosDB Details**: Update the `COSMOS_ENDPOINT`, `CONTAINER_NAME`, `DATABASE_NAME`, and `RESOURCE_GROUP` values as per your CosmosDB instance.
- **Azure Storage Details**: Specify the `STORAGE_ACCOUNT_NAME` and `STORAGE_CONTAINER` for the source of the restore operation.

## Example Workflow
Below is an example of how to configure the restore workflow:

- Ensure that the custom action `.github/actions/cosmosdb-backup` is implemented and available in the repository. Alternatively, replace it with a publicly available action in the format `org/repo@branch` if needed.

```yaml
name: Backup CosmosDB

on:
  workflow_dispatch:
  schedule:
    - cron: "0 2 * * *" # Every day at 2 AM UTC
  push:
    branches:
      - main

jobs:
  full_backup:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Full Backup CosmosDB to Azure Storage
        uses: ./.github/actions/cosmosdb-backup
        with:
          AZURE_CREDENTIALS: ${{ secrets.AZURE_CREDENTIALS }}
          ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
          ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
          ARM_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
          ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}
          COSMOS_ENDPOINT: "https://cosmos-cosmosdb-account-restore.documents.azure.com:443"
          COSMOS_KEY: ${{ secrets.COSMOS_KEY }}
          CONTAINER_NAME: "cosmos-container-src"
          DATABASE_NAME: "cosmos-database"
          RESOURCE_GROUP: "cosmos-resources"
          STORAGE_ACCOUNT_NAME: "cosmosbkp1123"
          STORAGE_CONTAINER: "cosmos-backup-container"
          action: "full_restore"
```

## Desired Output

After running the GitHub Action, you can verify the successful execution and inspect the output directly in the GitHub Actions logs.

### Example Output Image

Below is an example of how the output might look in the GitHub Actions interface:

![GitHub Action Output](./image/restore_output.png)

This image represents the logs and status of the backup process, including steps such as repository checkout, authentication, and the actual backup operation. Replace the placeholder image with a screenshot of your workflow's execution for better clarity.


## How to Locate Backup Files in Azure Storage

The backup files generated by the script are stored in the **Azure Storage Account** specified in the workflow. Below is a guide on how to locate these files:

### Steps to Locate Backup Files

1. **Access Azure Portal**:
 - Navigate to the **Storage Account** configured in the workflow (`STORAGE_ACCOUNT_NAME`).

2. **Find the Container**:
 - Inside the Storage Account, go to the **Containers** section.
 - Locate the container specified in the workflow (`STORAGE_CONTAINER`).

3. **Browse the Directory Structure**:
 - Inside the container, you will find directories organized by:
   - CosmosDB account name (`cosmos-account-name`).
   - Date and time of the backup (`YYYY-MM-DD-HHMM`).
   - Database name (`database-name`).
   - Container name (`container-name`).

4. **Locate the Backup File**:
 - Inside the container's directory, you will find the backup file with the following naming convention:
   ```
   cosmosdb_nosql_backup_<cosmos-account-name>_<database-name>_<container-name>_<timestamp>.json
   ```


## Running the Backup Script Locally

If you want to run the backup process locally without using GitHub Actions, you can execute the script manually by following these steps after clone the repo:

### Prerequisites

1. **Python Environment**:
   - Ensure you have Python 3.8 or later installed on your machine.
   - Install the required Python packages by running:
     ```bash
     pip install -r requirements.txt
     ```

2. **Azure CLI**:
   - Install and log in to the Azure CLI:
     ```bash
     az login
     ```

3. **Environment Variables**:
   - Set the required environment variables in your terminal. These variables are used by the script to authenticate and configure the backup process.

### Required Environment Variables

Set the following environment variables before running the script:

| Variable Name           | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| `COSMOS_ENDPOINT`       | The endpoint URL of the CosmosDB account.                                  |
| `COSMOS_KEY`            | The primary key for the CosmosDB account.                                  |
| `CONTAINER_NAME`        | The name of the CosmosDB container to back up.                             |
| `DATABASE_NAME`         | The name of the CosmosDB database to back up.                              |
| `RESOURCE_GROUP`        | The name of the Azure resource group containing the CosmosDB account.       |
| `STORAGE_ACCOUNT_NAME`  | The name of the Azure Storage account where the backup will be stored.      |
| `STORAGE_CONTAINER`     | The name of the Azure Storage container for the backup.                    |
| `SUBSCRIPTION_ID`       | The Azure subscription ID associated with the resources.                   |

### Example: Setting Environment Variables

Run the following commands in your terminal to set the environment variables:

```bash
export COSMOS_ENDPOINT="https://cosmos-cosmosdb-account.documents.azure.com:443/"
export COSMOS_KEY="your-cosmosdb-key"
export CONTAINER_NAME="cosmos-container-src"
export DATABASE_NAME="cosmos-database"
export RESOURCE_GROUP="cosmos-resources"
export STORAGE_ACCOUNT_NAME="cosmosbkp1123"
export STORAGE_CONTAINER="cosmos-backup-container"
export SUBSCRIPTION_ID="your-subscription-id"
```

### Running the Script
Once the environment variables are set, you can run the backup script:

```bash
cd python ./.github/actions/cosmosdb-restore full_restore.py
```