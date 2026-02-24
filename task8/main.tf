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

variable "student_id" { type = string }
variable "trigger_freq" { type = string } 
variable "retry_count" { type = number }

data "azurerm_resource_group" "rg" {
  name = "rg-course-${var.student_id}-ch1"
}

data "azurerm_data_factory" "adf" {
  name                = "adf-${var.student_id}-course"
  resource_group_name = data.azurerm_resource_group.rg.name
}

data "azurerm_synapse_workspace" "syn" {
  name                = "syn-${var.student_id}-dwh"
  resource_group_name = data.azurerm_resource_group.rg.name
}

data "azurerm_resources" "sa_list" {
  resource_group_name = data.azurerm_resource_group.rg.name
  type                = "Microsoft.Storage/storageAccounts"
}

locals {
  source_storage_name = [
    for s in data.azurerm_resources.sa_list.resources : s.name 
    if substr(s.name, 0, 5) != "stsyn"
  ][0]
}

data "azurerm_storage_account" "source_sa" {
  name                = local.source_storage_name
  resource_group_name = data.azurerm_resource_group.rg.name
}

resource "azurerm_storage_container" "raw" {
  name                  = "data"
  storage_account_name  = data.azurerm_storage_account.source_sa.name
  container_access_type = "private"
}

resource "azurerm_storage_blob" "seed_data" {
  name                   = "products.csv"
  storage_account_name   = data.azurerm_storage_account.source_sa.name
  storage_container_name = azurerm_storage_container.raw.name
  type                   = "Block"
  source                 = "${path.module}/../data/products.csv"
}

resource "azurerm_data_factory_linked_service_azure_blob_storage" "ls_blob" {
  name              = "LS_Source_Blob"
  data_factory_id   = data.azurerm_data_factory.adf.id
  connection_string = data.azurerm_storage_account.source_sa.primary_connection_string
}

resource "azurerm_data_factory_linked_service_synapse" "ls_synapse" {
  name                = "LS_Sink_Synapse"
  data_factory_id     = data.azurerm_data_factory.adf.id
  connection_string   = "Server=tcp:${data.azurerm_synapse_workspace.syn.connectivity_endpoints["sql"]},1433;Database=dwh_pool;"
}

resource "azurerm_data_factory_dataset_delimited_text" "ds_source" {
  name                = "ds_source_csv"
  data_factory_id     = data.azurerm_data_factory.adf.id
  linked_service_name = azurerm_data_factory_linked_service_azure_blob_storage.ls_blob.name

  azure_blob_storage_location {
    container = azurerm_storage_container.raw.name
    path      = ""
    filename  = "products.csv"
  }
  
  column_delimiter    = ","
  row_delimiter       = "\n"
  encoding            = "UTF-8"
  first_row_as_header = true
  quote_character     = "\""
  escape_character    = "\\"
}

resource "azurerm_data_factory_dataset_azure_sql_table" "ds_sink" {
  name              = "DS_Sink_Table"
  data_factory_id   = data.azurerm_data_factory.adf.id
  linked_service_id = azurerm_data_factory_linked_service_synapse.ls_synapse.id
  schema            = "dbo"
  table             = "Products"
}

resource "azurerm_data_factory_pipeline" "pl_copy" {
  name            = "PL_Copy_CSV_to_SQL"
  data_factory_id = data.azurerm_data_factory.adf.id

  depends_on = [
    azurerm_data_factory_dataset_delimited_text.ds_source,
    azurerm_data_factory_dataset_azure_sql_table.ds_sink
  ]
  
  activities_json = <<JSON
  [
    {
      "name": "CopyFromBlobToSynapse",
      "type": "Copy",
      "dependsOn": [],
      "policy": {
        "timeout": "0.12:00:00",
        "retry": ${var.retry_count},
        "retryIntervalInSeconds": 30,
        "secureOutput": false,
        "secureInput": false
      },
      "typeProperties": {
        "source": {
          "type": "DelimitedTextSource",
          "storeSettings": {
            "type": "AzureBlobStorageReadSettings",
            "recursive": true
          },
          "formatSettings": {
            "type": "DelimitedTextReadSettings"
          }
        },
        "sink": {
          "type": "SqlDWSink",
          "allowPolyBase": true,  
          "tableOption": "none",
          "disableMetricsCollection": false
        },
        "enableStaging": true,
        "stagingSettings": {
            "linkedServiceName": {
                "referenceName": "LS_Source_Blob",
                "type": "LinkedServiceReference"
            },
            "path": "data/staging"
        }
      },
      "inputs": [
        {
          "referenceName": "ds_source_csv",
          "type": "DatasetReference"
        }
      ],
      "outputs": [
        {
          "referenceName": "DS_Sink_Table",
          "type": "DatasetReference"
        }
      ]
    }
  ]
  JSON
}

resource "azurerm_data_factory_trigger_schedule" "trig" {
  name            = "daily_trigger"
  data_factory_id = data.azurerm_data_factory.adf.id
  pipeline_name   = azurerm_data_factory_pipeline.pl_copy.name
  interval        = 1
  frequency       = var.trigger_freq
  start_time      = "2024-01-01T02:00:00Z"
  activated       = true
}