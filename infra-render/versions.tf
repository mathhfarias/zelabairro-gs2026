terraform {
  required_version = ">= 1.6.0"
  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.9"
    }
  }
}

# Usa as variaveis de ambiente RENDER_API_KEY e RENDER_OWNER_ID.
provider "render" {}
