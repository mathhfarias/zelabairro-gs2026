# ZelaBairro — plano alternativo Azure Disabled → Render

## Cenário comprovado
- A assinatura Azure for Students retornou `Disabled`. O Terraform Azure não pode ser aplicado nela.
- O mesmo aplicativo Flask e o pipeline CI com Gitleaks/Semgrep/Trivy permanecem válidos.
- Há **dois caminhos alternativos** de provisionamento na Render: `infra-render/` via Terraform (**prioritário para tentar atender IaC**) ou `render.yaml` via Blueprint (mais rápido, mas **não demonstra Terraform apply**). **Escolha apenas um**.

## Pré-requisitos
1. Conta Render associada ao GitHub e permissão de conectar `https://github.com/mathhfarias/zelabairro-gs2026`.
2. Concordância explícita com cobrança do plano Starter + 1GB de disco. Verifique o preço atual na UI antes de provisionar.
3. Dockerfile configurado com Gunicorn em `0.0.0.0:8000`, sem root; `APP_ENV=production`; `DATABASE_PATH=/data/zelabairro.sqlite3`.
4. Atribuir senha de administrador forte, SECRET_KEY aleatória e METRICS_TOKEN aleatório (pelo menos 24 caracteres). **Nunca publicar esses valores**.

## Caminho A — Terraform Render (preferido na disciplina)
- Gere uma API key no painel da Render (Account Settings → API Keys) e encontre o Workspace Owner ID no painel. NÃO envie esses dados no chat.
- No Mac, em um terminal privado, defina `RENDER_API_KEY` e `RENDER_OWNER_ID` (use mecanismo seguro de variáveis de ambiente).
- Gere três valores distintos com `python3 -c 'import secrets; print(secrets.token_urlsafe(40))'` e defina `TF_VAR_secret_key`, `TF_VAR_admin_password`, `TF_VAR_metrics_token` como variáveis de ambiente local. Na descrição do PDF, não exponha essas variáveis.
- Execute:

```bash
cd ~/Desktop/zelabairro-gs2026/infra-render
terraform init
terraform fmt -check
terraform validate
terraform plan -out=render.tfplan
# Rever custo e recursos antes de aplicar
terraform apply render.tfplan
terraform output url_zela_bairro
```

Se o provider informar algum argumento incompatível com a versão instalada, use as orientações do `terraform validate` e a [documentação oficial do recurso web_service](https://registry.terraform.io/providers/render-oss/render/latest/docs/resources/web_service). **A configuração deste pacote é proposta e não foi aplicada numa conta Render nesta sessão.**

A Render oferece provider oficial `render-oss/render`; ele é diferente do provider `hashicorp/azurerm`. Não rodar `terraform apply` no diretório `infra/` Azure.

⚠️ SEGURANÇA DE STATE: valores sensíveis podem ficar armazenados em `terraform.tfstate` e plano. Ambos já estão excluídos por `.gitignore`; confira `git status --ignored`. Não envie essas evidências com conteúdo sensível. Prefira recortar logs sem dados pessoais.

## Caminho B — Blueprint Render (fallback rápido, não comprova Terraform)
- Mantenha o arquivo `render.yaml` na raiz e publique com `git add render.yaml && git commit ... && git push`.
- Em https://dashboard.render.com/, escolha New > Blueprint e selecione repositório e branch.
- Confirme preço do Starter + disco, e forneça `ADMIN_PASSWORD` quando solicitado. As outras variáveis secretas serão geradas pela Render.
- Escolha Auto Deploy **After CI Checks Pass**; verifique se a plataforma está observando os checks da branch `main`.
- Teste `/health`, cadastro, consulta e **reinício ou redeploy** para verificar persistência.
- Se aparecer `sqlite3.OperationalError: unable to open database file`, o volume em `/data` não está gravável para o UID 10001 do container. **Não execute `chmod 777` no disco e não passe o container para root**: diagnostique permissões no serviço e ajuste propriedade/mount com suporte/configuração apropriada.

## Comparação importante
- Render gratuito **não oferece disco persistente**. Cadastro gravado em SQLite pode sumir no restart/deploy. Use gratuito apenas como prova de navegação, deixando essa limitação explícita; não descreva persistência de produção como validada.
- Um plano pago com disco e testes de reinício oferece persistência real, mas precisa confirmar cobrança e funcionamento.
- A publicação pelo Render Dashboard não cria automaticamente a evidência de **Terraform aplicado**. Para a rubrica IaC é necessário executar o Caminho A e guardar `init`, `validate`, `plan` e `apply` com sucesso.

## Monitoramento
- No arquivo `monitoring/prometheus.yml` local, substitua o alvo Azure pela URL `SEU_APP.onrender.com:443`; use `scheme: https`, `metrics_path: /metrics`, bearer token em `monitoring/metrics_token`.
- Se escolheu Blueprint, guarde o token num local seguro e configure o mesmo `METRICS_TOKEN` no serviço e no arquivo local de monitoramento; cuidado para não perder o token gerado automaticamente.
- `docker compose up -d` em `monitoring/`; Grafana http://127.0.0.1:3000 e Prometheus http://127.0.0.1:9090/targets.
- Gere tráfego e faça um teste de alerta controlado, registrando antes/depois.

## Evidências FIAP
- Print dos jobs de CI (bloqueado e corrigido), link de repositório, URL pública, tela de cadastro e consulta, logs de deploy.
- Para IaC, prints reais `terraform validate`, `plan`, `apply` e recursos ativos. Não confundir código Terraform com provisionamento executado.
- Quatro métricas de ouro, alerta `Firing`, custos, LGPD, responsabilidade compartilhada e ficha técnica.

Fontes: https://render.com/docs/terraform-provider , https://render.com/docs/disks , https://render.com/docs/deploys , https://render.com/docs/blueprint-spec .
