variable "subscription_id" {
  description = "ID da assinatura Azure; nunca publicar arquivos de estado ou tfvars."
  type        = string
  sensitive   = true
}
variable "location" {
  description = "Regiao Azure do App Service."
  type        = string
  default     = "brazilsouth"
}
variable "name_prefix" {
  description = "Prefixo minusculo para nomes do app."
  type        = string
  default     = "zelabairro-gs"
}
variable "image_repository" {
  description = "Imagem GHCR publicada pelo GitHub Actions."
  type        = string
  default     = "mathhfarias/zelabairro-gs2026"
}
variable "sku_name" {
  description = "Plano Linux pago; B1 e adequado somente para demonstracao e possui custo."
  type        = string
  default     = "B1"
}
