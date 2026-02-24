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
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
}

data "azurerm_client_config" "current" {}

variable "student_id" {
  type        = string
  description = "Unique identifier for the student"
}

variable "location" {
  type    = string
  default = "westeurope"
}

variable "kv_sku" {
  type    = string
  default = "standard"
}

resource "random_id" "rn" {
  byte_length = 4
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-course-${var.student_id}-ch1"
  location = var.location
}

resource "azurerm_storage_account" "sa" {
  name                     = "sa${substr(replace(var.student_id, "-", ""), 0, 10)}${random_id.rn.hex}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true
}

resource "azurerm_key_vault" "kv" {
  name                        = "kv-${substr(replace(var.student_id, "-", ""), 0, 10)}-${random_id.rn.hex}"
  location                    = azurerm_resource_group.rg.location
  resource_group_name         = azurerm_resource_group.rg.name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false
  
  sku_name                    = lower(var.kv_sku)

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = [
      "Get", "List", "Create", "Delete", "Update",
    ]

    secret_permissions = [
      "Get", "List", "Set", "Delete",
    ]

    storage_permissions = [
      "Get", "List",
    ]
  }
}

output "rg_name" {
  value = azurerm_resource_group.rg.name
}