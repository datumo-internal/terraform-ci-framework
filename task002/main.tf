resource "azurerm_resource_group" "szkolenie" {
  name     = local.final_rg_name
  location = var.location
} 