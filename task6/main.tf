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
  type        = string
  description = "Your ID (ex. janmarek-dm)"
}

variable "log_retention" {
  type        = number
  description = "How many days keep logs"
}

variable "daily_quota_gb" {
  type        = number
  description = "Daily imit GB (-1 means no limit)"
}

data "azurerm_resource_group" "rg" {
  name = "rg-course-${var.student_id}-ch1"
}

data "azurerm_data_factory" "adf" {
  name                = "adf-${var.student_id}-course"
  resource_group_name = data.azurerm_resource_group.rg.name
}

resource "azurerm_log_analytics_workspace" "law" {
  name                = "law-${var.student_id}"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = var.log_retention
  
  daily_quota_gb      = var.daily_quota_gb == -1 ? null : var.daily_quota_gb
}

resource "azurerm_monitor_diagnostic_setting" "adf_logs" {
  name                       = "adf-to-law-diag"
  target_resource_id         = data.azurerm_data_factory.adf.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id

  enabled_log {
    category = "PipelineRuns"
  }
  enabled_log {
    category = "ActivityRuns"
  }
  metric {
    category = "AllMetrics"
  }
}