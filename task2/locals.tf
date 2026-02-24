locals {
  rg_name                   = "${var.project}-${var.environment}-rg"
  storage_name              = "tf${var.project}${var.environment}sa"
  databricks_workspace_name = "${var.project}-${var.environment}-databricks-ws"

  common_tags = {
    project     = var.project
    environment = var.environment
  }
}