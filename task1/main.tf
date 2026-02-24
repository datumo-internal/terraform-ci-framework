resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = var.location
  tags     = local.common_tags

}

resource "azurerm_storage_account" "storageaccount" {
  name                     = local.storage_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = var.account_tier
  account_replication_type = "GRS"

  tags = local.common_tags
}

/*
resource "azurerm_databricks_workspace" "databricksworkspace" {
  name                = local.databricks_workspace_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "standard"

  tags = local.common_tags
}
*/