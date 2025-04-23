# Backup CosmosDB GitHub Action

![CosmosDB Backup](https://markpatton.cloud/wp-content/uploads/2020/03/definingbackuppolicycosmosdb-img-e1585163856238.png)

This GitHub Action automates the process of backing up a CosmosDB database to Azure Storage. It is designed to run on a schedule or be triggered manually via the `workflow_dispatch` event .

## Workflow example Overview

- **Name**: Backup CosmosDB
- **Triggers**:
    - Scheduled to run daily at 2 AM UTC.
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
                    action: "backup"
```

## Notes - New


- Ensure that the Azure credentials and CosmosDB keys are securely stored as GitHub secrets.
- Update the `cron` expression in the `schedule` section to adjust the backup frequency based on your requirements. For example, to run the backup every 6 hours, use `0 */6 * * *`.
- Ensure that the custom action `.github/actions/cosmosdb-backup` is implemented and available in the repository. Alternatively, replace it with a publicly available action in the format `org/repo@branch` if needed.
# cosmos-nosql-bkp