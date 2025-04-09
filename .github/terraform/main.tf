terraform {
    required_providers {
        azurerm = {
            source  = "hashicorp/azurerm"
 #           version = "3.75.0"
        }
    }
}

provider "azurerm" {
    features {
        resource_group {
            prevent_deletion_if_contains_resources = false
        }
    }
}

resource "azurerm_resource_group" "cosmos-db-rg" {
    name     = "cosmos-resources"
    location = "East US2"
tags = {
        BU        = "DIGITAL"
        AMBIENTE  = "DEV"
        CC        = "123456"
        CCOWNER   = "owner@example.com"
    }
}

resource "azurerm_cosmosdb_account" "cosmos-db-account" {
    name                       = "cosmos-cosmosdb-account"
    location                   = azurerm_resource_group.cosmos-db-rg.location
    resource_group_name        = azurerm_resource_group.cosmos-db-rg.name
    offer_type                 = "Standard"
    kind                       = "GlobalDocumentDB"
   # enable_automatic_failover  = false
    tags = {
        BU        = "DIGITAL"
        AMBIENTE  = "DEV"
        CC        = "123456"
        CCOWNER   = "owner@example.com"
    }
    geo_location {
        location          = azurerm_resource_group.cosmos-db-rg.location
        failover_priority = 0
    }

    consistency_policy {
        consistency_level       = "BoundedStaleness"
        max_interval_in_seconds = 300
        max_staleness_prefix    = 100000
    }

    capabilities {
        name = "EnableServerless"
    }

    depends_on = [
        azurerm_resource_group.cosmos-db-rg
    ]
}

resource "azurerm_cosmosdb_sql_database" "cosmos-db" {
    name                = "cosmos-database"
    resource_group_name = azurerm_resource_group.cosmos-db-rg.name
    account_name        = azurerm_cosmosdb_account.cosmos-db-account.name
}

resource "azurerm_cosmosdb_sql_container" "cosmos-container" {
    name                = "cosmos-container-src"
    resource_group_name = azurerm_resource_group.cosmos-db-rg.name
    account_name        = azurerm_cosmosdb_account.cosmos-db-account.name
    database_name       = azurerm_cosmosdb_sql_database.cosmos-db.name
    partition_key_paths  = ["/partitionKey"]
    #throughput          = 400
}

resource "azurerm_cosmosdb_sql_container" "cosmos-containerdst" {
    name                = "cosmos-container-dst"
    resource_group_name = azurerm_resource_group.cosmos-db-rg.name
    account_name        = azurerm_cosmosdb_account.cosmos-db-account.name
    database_name       = azurerm_cosmosdb_sql_database.cosmos-db.name
    partition_key_paths  = ["/partitionKey"]
    #throughput          = 400
}




resource "azurerm_storage_account" "backup_storage_account" {
    name                     = "cosmosbkpxpto"
    resource_group_name      = azurerm_resource_group.cosmos-db-rg.name
    location                 = azurerm_resource_group.cosmos-db-rg.location
    account_tier             = "Standard"
    account_replication_type = "LRS"
    tags = {
        BU        = "DIGITAL"
        AMBIENTE  = "DEV"
        CC        = "123456"
        CCOWNER   = "owner@example.com"
    }
}

resource "azurerm_storage_container" "backup_container" {
    name                  = "cosmos-backup-container"
    storage_account_name  = azurerm_storage_account.backup_storage_account.name
    container_access_type = "private"
}


#############################################
####   EXPORTS FOR COSMOS DB BACKUP   ####
#############################################



output "COSMOSDB_ENDPOINT" {
    description = "The endpoint of the CosmosDB Account"
    value       = azurerm_cosmosdb_account.cosmos-db-account.endpoint
}

output "COSMOSDB_PRIMARY_MASTER_KEY" {
    description = "The primary master key of the CosmosDB Account"
    value       = azurerm_cosmosdb_account.cosmos-db-account.primary_key
    sensitive   = true
}

output "STORAGE_ACCOUNT_NAME" {
    description = "The name of the Storage Account for backups"
    value       = azurerm_storage_account.backup_storage_account.name
}

output "STORAGE_CONTAINER_NAME" {
    description = "The name of the Storage Container for backups"
    value       = azurerm_storage_container.backup_container.name
}

output "DATABASE_NAME" {
    description = "The name of the Cosmos DB database"
    value       = azurerm_cosmosdb_sql_database.cosmos-db.name
}

output "CONTAINER_NAME" {
    description = "The name of the Cosmos DB container"
    value       = azurerm_cosmosdb_sql_container.cosmos-container.name
}

output "SUBSCRIPTION_ID" {
    description = "The Azure subscription ID"
    value       = data.azurerm_client_config.current.subscription_id
}

output "RESOURCE_GROUP" {
    description = "The name of the resource group"
    value       = azurerm_resource_group.cosmos-db-rg.name
}

data "azurerm_client_config" "current" {}


