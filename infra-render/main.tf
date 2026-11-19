# Alternativa a infra/ (Azure). Execute SOMENTE UM dos dois destinos.
# Pago: plano Starter + disco persistente (ver custo no painel Render).
resource "render_web_service" "zelabairro" {
  name   = var.service_name
  plan   = "starter"
  region = "ohio"

  runtime_source = {
    docker = {
      repo_url            = "https://github.com/mathhfarias/zelabairro-gs2026"
      branch              = "main"
      auto_deploy_trigger = "checksPass"
    }
  }

  # O SQLite do Dockerfile grava em /data/zelabairro.sqlite3.
  disk = {
    name       = "zelabairro-sqlite"
    mount_path = "/data"
    size_gb    = 1
  }

  env_vars = {
    APP_ENV       = { value = "production" }
    DATABASE_PATH = { value = "/data/zelabairro.sqlite3" }
    PORT          = { value = "8000" }
    SECRET_KEY    = { value = var.secret_key }
    ADMIN_PASSWORD = { value = var.admin_password }
    METRICS_TOKEN = { value = var.metrics_token }
  }
}

output "url_zela_bairro" {
  description = "URL prevista apos a Render provisionar o web service"
  value       = "https://${render_web_service.zelabairro.slug}.onrender.com"
}
