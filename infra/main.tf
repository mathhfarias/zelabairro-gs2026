resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}
locals {
  suffix = random_string.suffix.result
  app    = "${var.name_prefix}-${local.suffix}"
  rg     = "rg-${local.app}"
}
resource "azurerm_resource_group" "project" {
  name     = local.rg
  location = var.location
}
resource "azurerm_service_plan" "project" {
  name                = "asp-${local.app}"
  resource_group_name = azurerm_resource_group.project.name
  location            = azurerm_resource_group.project.location
  os_type             = "Linux"
  sku_name            = var.sku_name
}
resource "azurerm_linux_web_app" "project" {
  name                = local.app
  resource_group_name = azurerm_resource_group.project.name
  location            = azurerm_resource_group.project.location
  service_plan_id     = azurerm_service_plan.project.id
  https_only          = true
  client_affinity_enabled = false
  app_settings = {
    APP_ENV                         = "production"
    DATABASE_PATH                   = "/home/zelabairro.sqlite3"
    WEBSITES_PORT                   = "8000"
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = "true"
  }
  site_config {
    always_on           = true
    ftps_state          = "Disabled"
    http2_enabled       = true
    minimum_tls_version = "1.2"
    health_check_path   = "/health"
    application_stack {
      docker_registry_url = "https://ghcr.io"
      docker_image_name   = "${var.image_repository}:latest"
    }
  }
  lifecycle {
    # Segredos inseridos fora do Terraform pelo Azure CLI, e tag por CI/CD.
    # A configuracao remota e preservada para nao sobrescrever esses valores.
    ignore_changes = [app_settings, site_config[0].application_stack[0].docker_image_name]
  }
}
