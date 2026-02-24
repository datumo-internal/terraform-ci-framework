locals {
  prefix        = var.username != "" ? substr(var.username, 0, 4) : ""
  rg_name = "${local.prefix}-${var.resource_group_name}"
}
