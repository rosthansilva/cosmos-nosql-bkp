# Backup CosmosDB GitHub Action

![CosmosDB Backup](https://markpatton.cloud/wp-content/uploads/2020/03/definingbackuppolicycosmosdb-img-e1585163856238.png)

**CosmosDB Full Backup and Restore with GitHub Actions**  
This repository contains workflows to perform full backup and full restore of CosmosDB databases using GitHub Actions. Below, you will find detailed instructions.

---

## 🚀 How to Use the Full Backup Workflow

The Full Backup workflow performs a backup of all databases and containers in a CosmosDB account and stores the data in Azure Blob Storage.

### 📋 Prerequisites

Configure the Secrets in the GitHub repository:

- `AZURE_CREDENTIALS`: Azure credentials in JSON format.
- `ARM_CLIENT_ID`, `ARM_CLIENT_SECRET`, `ARM_SUBSCRIPTION_ID`, `ARM_TENANT_ID`: Azure Resource Manager details.
- `COSMOS_KEY`: Access key for CosmosDB.
- `STORAGE_ACCOUNT_NAME`, `STORAGE_CONTAINER`: Azure Storage account details.

Ensure that CosmosDB and Azure Blob Storage are properly configured.

### 🛠️ Workflow Configuration

The workflow file is located at:  
📂 `backup-cosmosdb.yml`

#### Example of Full Backup Execution:

```yaml
name: Full Backup CosmosDB

on:
  workflow_dispatch: # Allows manual execution
  schedule:
    - cron: "0 2 * * *" # Runs daily at 2 AM UTC

jobs:
  full_backup:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Full Backup CosmosDB to Azure Storage
        uses: ./.github/actions/cosmosdb-backup
        with:
          AZURE_CREDENTIALS: ${{ secrets.AZURE_CREDENTIALS }}
          ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
          ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
          ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}
          ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}
          COSMOS_ENDPOINT: "https://<cosmosdb-account>.documents.azure.com:443"
          COSMOS_KEY: ${{ secrets.COSMOS_KEY }}
          RESOURCE_GROUP: "cosmos-resources"
          STORAGE_ACCOUNT_NAME: "cosmosbkp1123"
          STORAGE_CONTAINER: "cosmos-backup-container"
          action: "full_backup"
```

### ▶️ How to Execute

1. Go to the **Actions** tab in the GitHub repository.
2. Select the **Full Backup CosmosDB** workflow.
3. Click **Run workflow** and wait for execution.

---

## 🔄 How to Use the Full Restore Workflow

The Full Restore workflow restores all databases and containers from a backup stored in Azure Blob Storage to a CosmosDB account.

### 📋 Prerequisites

Configure the Secrets in the GitHub repository:

- `AZURE_CREDENTIALS`: Azure credentials in JSON format.
- `ARM_CLIENT_ID`, `ARM_CLIENT_SECRET`, `ARM_SUBSCRIPTION_ID`, `ARM_TENANT_ID`: Azure Resource Manager details.
- `COSMOS_KEY`: Access key for CosmosDB.
- `STORAGE_ACCOUNT_NAME`, `STORAGE_CONTAINER`: Azure Storage account details.

Ensure that the backup has been previously performed and is available in Azure Blob Storage.

### 🛠️ Workflow Configuration

The workflow file is located at:  
📂 `restore-cosmosdb.yml`

#### Example of Full Restore Execution:

```yaml
name: Full Restore CosmosDB

on:
  workflow_dispatch: # Allows manual execution

jobs:
  full_restore:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Full Restore CosmosDB from Azure Storage
        uses: ./.github/actions/cosmosdb-restore
        with:
          AZURE_CREDENTIALS: ${{ secrets.AZURE_CREDENTIALS }}
          ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
          ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
          ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}
          ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}
          COSMOS_ENDPOINT: "https://<cosmosdb-account>.documents.azure.com:443"
          COSMOS_KEY: ${{ secrets.COSMOS_KEY }}
          RESOURCE_GROUP: "cosmos-resources"
          STORAGE_ACCOUNT_NAME: "cosmosbkp1123"
          STORAGE_CONTAINER: "cosmos-backup-container"
          action: "full_restore"
```

### ▶️ How to Execute

1. Go to the **Actions** tab in the GitHub repository.
2. Select the **Full Restore CosmosDB** workflow.
3. Click **Run workflow** and wait for execution.

---

## 📝 Notes

- **Logs**: During execution, workflow logs will be available in the **Actions** tab.
- **Errors**: If an error occurs, check the logs to identify the issue.
- **Scheduling**: You can configure workflow scheduling using cron syntax.
