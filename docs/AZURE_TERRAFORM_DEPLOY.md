# ZelaBairro — Terraform + GitHub Actions + Azure

**O mesmo projeto Flask é usado nas disciplinas Secure DevOps e Startup.**
Esta extensão não modifica o objetivo de produto, as rotas públicas nem o contrato da entidade ocorrência.

## O que foi feito e o que ainda precisa de execução real

Este pacote contém código de Terraform, publicação no GHCR, deploy por OIDC e dashboard Prometheus/Grafana. **Os recursos Azure não foram criados a partir deste ambiente**: é necessário executar os comandos abaixo na assinatura do grupo. Não declarar no PDF que foi implantado antes de tirar prints reais.

### 1. Pré-requisitos
- Git, Docker Desktop, Terraform >= 1.6, Azure CLI (`az`), assinatura Azure com permissão de criar RG e App Service B1. **B1 gera cobrança enquanto ativo**, mesmo sem tráfego.
- Repositório `mathhfarias/zelabairro-gs2026` clonado com `git clone`, não Download ZIP.
- Azure para estudantes pode ter cotas/regiões restritas. Não assumir que B1 está disponível.

### 2. Versionar os novos arquivos
```bash
cd ~/Desktop/zelabairro-gs2026
python3 -m compileall -q app tests wsgi.py
git status
git add app Dockerfile tests .github infra monitoring docs README.md .gitignore
git commit -m "feat: Terraform Azure, GHCR e monitoramento do ZelaBairro"
git push origin main
```
Aguarde todos os jobs, **inclusive Publicar imagem no GHCR**. Em GitHub > Packages, configure a imagem `zelabairro-gs2026` como **Public**, pois o Azure irá baixá-la sem credenciais de registro. Caso haja restrição de publicação pública, não exponha token GHCR no código; escolha ACR com identidade gerenciada posteriormente.

### 3. Provisionar com Terraform
No Mac, instale Azure CLI e Terraform pelas páginas oficiais. Faça login:
```bash
az login
az account list -o table
az account set --subscription "ID_DA_ASSINATURA"
cd ~/Desktop/zelabairro-gs2026/infra
cp terraform.tfvars.example terraform.tfvars
# Edite terraform.tfvars com subscription_id e location.
terraform init
terraform fmt -check
terraform validate
terraform plan -out=deploy.tfplan
terraform apply deploy.tfplan
terraform output
```
Não publique `terraform.tfvars`, `terraform.tfstate`, `deploy.tfplan` ou arquivos de estado. O state local é importante para destruir os recursos depois; mantenha uma cópia protegida fora do Git. Antes de `apply`, revise os recursos e custos.

### 4. Configurar secrets do Flask no Azure
O aplicativo não inicia em produção sem SECRET_KEY, ADMIN_PASSWORD e METRICS_TOKEN. Insira-os **depois do terraform apply** e antes de testar a URL:
```bash
cd ~/Desktop/zelabairro-gs2026/infra
RG=$(terraform output -raw resource_group_name)
APP=$(terraform output -raw web_app_name)
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
METRICS_TOKEN=$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')
printf 'Senha administrativa forte: '; read -s ADMIN_PASSWORD; echo
az webapp config appsettings set --resource-group "$RG" --name "$APP"  --settings "SECRET_KEY=$SECRET_KEY" "ADMIN_PASSWORD=$ADMIN_PASSWORD" "METRICS_TOKEN=$METRICS_TOKEN"  --output none
# Guardar token SOMENTE no arquivo local ignorado pelo Git:
printf '%s' "$METRICS_TOKEN" > ../monitoring/metrics_token
chmod 600 ../monitoring/metrics_token
unset SECRET_KEY ADMIN_PASSWORD METRICS_TOKEN
az webapp restart --resource-group "$RG" --name "$APP"
URL=$(terraform output -raw public_url)
curl -i "$URL/health"
```
Confira um cadastro e sua consulta, reinicie o App Service e repita a consulta para validar persistência. Se o banco em `/home` não for gravável pelo usuário não-root, os logs informarão `PermissionError`: nesse caso, pare e escolha armazenamento com permissões adequadas; **não troque para /tmp**, pois a persistência sumiria. O SQLite em storage compartilhado é apenas demonstração com instância única, não arquitetura para escala de produção.

### 5. Preparar GitHub OIDC para deploy automático
A configuração de federação é uma atividade administrativa no Microsoft Entra ID. Crie um App Registration para GitHub Actions, registre o `Application (client) ID` e o `Directory (tenant) ID`, configure uma Federated Credential:
- **Issuer:** `https://token.actions.githubusercontent.com`
- **Subject:** `repo:mathhfarias/zelabairro-gs2026:ref:refs/heads/main`
- **Audience:** `api://AzureADTokenExchange`

Associe a identidade com o papel **Website Contributor** no recurso Web App específico. A criação de identidades e atribuições exige permissão administrativa; se não tiver, peça ao responsável Azure para realizar a etapa.

**Atalho opcional (Azure CLI + GitHub CLI autenticados):** após `terraform apply`, rode `bash scripts/setup_azure_oidc.sh` a partir da raiz do projeto. O script cria uma identidade federada exclusiva para a branch `main`, limita o papel ao Web App e configura secrets/variables no GitHub. Execute uma única vez. Se sua conta não puder criar App Registration ou role assignment, siga a configuração manual com o administrador. Antes de rodar, examine o script para entender quais recursos e permissões ele cria.

No repositório GitHub > Settings > Secrets and variables > Actions:
- **Secrets:** `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` (IDs são identificadores; Secrets aqui simplificam o setup).
- **Variable:** `AZURE_WEBAPP_NAME` = resultado de `terraform output -raw web_app_name`.

Faça um commit pequeno na `main` para iniciar publicação+deploy automático. O deploy só roda se o gate estiver verde e `AZURE_WEBAPP_NAME` estiver definido.

### 6. Provar CI/CD (guardar prints)
- Workflow bloqueado pela detecção original do Semgrep ou Trivy e commit com correção.
- Workflow verde com testes, Gitleaks, Semgrep, Trivy e gate.
- Job de publicação da imagem no GHCR.
- Terraform `plan/apply` (com dados sensíveis ocultos).
- Job `deploy-azure` verde e URL pública.
- `/health` acessível e registro que persiste após reiniciar.

### 7. Custo e desligamento
O plano Linux B1 pode gerar custo por hora, além de armazenamento e eventual tráfego. Veja o preço na calculadora oficial da Azure **antes** de criar, e registre a estimativa para a rubrica. Para desligar recursos pagos após a avaliação:
```bash
cd ~/Desktop/zelabairro-gs2026/infra
terraform destroy
```
Os links públicos devem ficar ativos durante a correção, segundo o enunciado FIAP. Remover o RG apagará dados da aplicação; faça backup de dados de teste autorizados antes, se necessário.

### Referências
- https://learn.microsoft.com/azure/app-service/configure-custom-container
- https://learn.microsoft.com/en-us/azure/app-service/deploy-container-github-action
- https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/linux_web_app
