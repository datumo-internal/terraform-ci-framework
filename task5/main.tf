terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  backend "azurerm" {}
}

provider "azurerm" {
  features {}
}

variable "student_id" {
  type = string
}

variable "adf_public_access" {
  type        = bool
  description = "Czy ADF ma być dostępny publicznie? (Zadanie 1)"
}

variable "adf_identity_type" {
  type        = string
  description = "Typ tożsamości: SystemAssigned lub None (Zadanie 2)"
}

data "azurerm_resource_group" "rg" {
  name = "rg-course-${var.student_id}-ch1"
}

resource "azurerm_data_factory" "adf" {
  name                = "adf-${var.student_id}-course"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  
  public_network_enabled = var.adf_public_access

  identity {
    type = var.adf_identity_type
  }
}

output "adf_name" {
  value = azurerm_data_factory.adf.name
}