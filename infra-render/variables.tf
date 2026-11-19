variable "service_name" {
  description = "Identificador publico exclusivo na Render"
  type        = string
  default     = "zelabairro-gs2026-mathh"
}

variable "admin_password" {
  description = "Senha do painel administrativo; nunca versionar"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Chave secreta Flask com pelo menos 32 bytes aleatorios"
  type        = string
  sensitive   = true
}

variable "metrics_token" {
  description = "Bearer token do endpoint /metrics"
  type        = string
  sensitive   = true
}
