terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
  backend "azurerm" {}
}

provider "azurerm" {
  features {}
}

variable "student_id" { type = string }
variable "synapse_sku" { type = string }
variable "storage_repl" { type = string }

data "azurerm_resource_group" "rg" {
  name = "rg-course-${var.student_id}-ch1"
}

data "azurerm_client_config" "current" {}

resource "random_password" "sql_pass" {
  length  = 16
  special = true
  numeric = true
  upper   = true
  lower   = true
}

resource "random_id" "rn" {
  byte_length = 4
}

# 1. Storage Account (Data Lake)
resource "azurerm_storage_account" "syn_sa" {
  name                     = "stsyn${substr(replace(var.student_id, "-", ""), 0, 10)}${random_id.rn.hex}"
  resource_group_name      = data.azurerm_resource_group.rg.name
  location                 = "northeurope"
  account_tier             = "Standard"
  account_replication_type = var.storage_repl
  account_kind             = "StorageV2"
  is_hns_enabled           = true
}

# 2. System plików
resource "azurerm_storage_data_lake_gen2_filesystem" "syn_fs" {
  name               = "synapse-data"
  storage_account_id = azurerm_storage_account.syn_sa.id
}

# 3. Workspace Synapse
resource "azurerm_synapse_workspace" "syn" {
  name                                 = "syn-${var.student_id}-dwh"
  resource_group_name                  = data.azurerm_resource_group.rg.name
  location                             = "northeurope"
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.syn_fs.id
  sql_administrator_login              = "sqladminuser"
  sql_administrator_login_password     = random_password.sql_pass.result

  identity {
    type = "SystemAssigned"
  }
}

# 4. Firewall Rule - Dostęp dla Ciebie (Allow All)
resource "azurerm_synapse_firewall_rule" "allow_all" {
  name                 = "AllowAll"
  synapse_workspace_id = azurerm_synapse_workspace.syn.id
  start_ip_address     = "0.0.0.0"
  end_ip_address       = "255.255.255.255"
}

# 5. Firewall Rule - Dostęp dla usług Azure (Data Factory)
resource "azurerm_synapse_firewall_rule" "allow_azure_services" {
  name                 = "AllowAllWindowsAzureIps"
  synapse_workspace_id = azurerm_synapse_workspace.syn.id
  start_ip_address     = "0.0.0.0"
  end_ip_address       = "0.0.0.0"
}

# 6. SQL Pool
resource "azurerm_synapse_sql_pool" "dwh" {
  name                 = "dwh_pool"
  synapse_workspace_id = azurerm_synapse_workspace.syn.id
  sku_name             = var.synapse_sku
  create_mode          = "Default"
}