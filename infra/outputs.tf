output "resource_group_name" {
  value       = azurerm_resource_group.project.name
  description = "Grupo de recursos do MVP."
}
output "web_app_name" {
  value       = azurerm_linux_web_app.project.name
  description = "Adicionar em Settings > Secrets and variables > Actions > Variables como AZURE_WEBAPP_NAME."
}
output "public_url" {
  value       = "https://${azurerm_linux_web_app.project.default_hostname}"
  description = "URL HTTPS publica; so funciona apos configurar secrets e imagem publica."
}
