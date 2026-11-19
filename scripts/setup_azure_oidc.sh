#!/usr/bin/env bash
# Cria identidade federada do GitHub Actions na Azure, com escopo APENAS do Web App.
# Requisitos: az login, terraform apply, gh auth login e permissão de criar app e role assignment.
set -euo pipefail
REPO="mathhfarias/zelabairro-gs2026"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for x in az terraform gh python3; do
  if ! command -v "$x" >/dev/null 2>&1; then echo "Instale a ferramenta obrigatória: $x" >&2; exit 1; fi
done
az account show --output none || { echo 'Execute: az login' >&2; exit 1; }
gh auth status >/dev/null || { echo 'Execute: gh auth login' >&2; exit 1; }
cd "$ROOT/infra"
RG="$(terraform output -raw resource_group_name)"
APP="$(terraform output -raw web_app_name)"
SUBSCRIPTION="$(az account show --query id -o tsv)"
TENANT="$(az account show --query tenantId -o tsv)"
WEBAPP_SCOPE="$(az webapp show --resource-group "$RG" --name "$APP" --query id -o tsv)"
if [[ -z "$RG" || -z "$APP" || -z "$SUBSCRIPTION" || -z "$TENANT" || -z "$WEBAPP_SCOPE" ]]; then
  echo 'Não foi possível identificar a infraestrutura; execute terraform apply primeiro.' >&2
  exit 1
fi
printf 'App Service: %s | Resource Group: %s\n' "$APP" "$RG"
# Registra uma nova aplicação de serviço para este projeto acadêmico.
CLIENT_ID="$(az ad app create --display-name "zelabairro-github-deploy-${APP}" --query appId -o tsv)"
SP_OBJECT_ID="$(az ad sp create --id "$CLIENT_ID" --query id -o tsv)"
TMP_FILE="$(mktemp)"
trap 'rm -f "$TMP_FILE"' EXIT
python3 - "$TMP_FILE" "$REPO" <<'PY'
import json, sys
with open(sys.argv[1], 'w', encoding='utf-8') as f:
    json.dump({
        'name': 'github-main',
        'issuer': 'https://token.actions.githubusercontent.com',
        'subject': f'repo:{sys.argv[2]}:ref:refs/heads/main',
        'description': 'CI/CD do ZelaBairro na branch main',
        'audiences': ['api://AzureADTokenExchange'],
    }, f)
PY
az ad app federated-credential create --id "$CLIENT_ID" --parameters "$TMP_FILE" --output none
# Papel limitado ao recurso App Service, não à assinatura.
az role assignment create \
  --assignee-object-id "$SP_OBJECT_ID" \
  --assignee-principal-type ServicePrincipal \
  --role 'Website Contributor' \
  --scope "$WEBAPP_SCOPE" --output none
# Esses são IDs de configuração, não tokens de acesso.
printf '%s' "$CLIENT_ID" | gh secret set AZURE_CLIENT_ID --repo "$REPO"
printf '%s' "$TENANT" | gh secret set AZURE_TENANT_ID --repo "$REPO"
printf '%s' "$SUBSCRIPTION" | gh secret set AZURE_SUBSCRIPTION_ID --repo "$REPO"
gh variable set AZURE_WEBAPP_NAME --body "$APP" --repo "$REPO"
echo "Identidade OIDC configurada. Repositório: $REPO; aplicativo: $APP"
echo 'Faça um push na main para disparar a publicação e o deploy. Confira a execução no GitHub Actions.'
