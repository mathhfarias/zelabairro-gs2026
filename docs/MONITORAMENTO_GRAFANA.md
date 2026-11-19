# Monitoramento do ZelaBairro — Prometheus + Grafana

Este kit coleta métricas de uma URL Azure pública protegida por bearer token. **Não afirme que o painel ou o alerta foram executados até testar de verdade.**

## Antes de iniciar
- A URL Azure deve responder a `/health` e ter `METRICS_TOKEN` configurado no ambiente.
- Em `monitoring/`, copie `prometheus.yml.example` para `prometheus.yml` e troque `SEU_APP.azurewebsites.net:443` pelo endereço real do Terraform.
- O token utilizado no Azure deve estar no arquivo local `monitoring/metrics_token` (sem linha final), não versionado.
- Copie `.env.example` para `.env` e defina uma senha forte e distinta de `ADMIN_PASSWORD`.

```bash
cd ~/Desktop/zelabairro-gs2026/monitoring
cp prometheus.yml.example prometheus.yml
cp .env.example .env
# Editar o alvo HTTPS e a senha no editor.
docker compose up -d
docker compose ps
```

Abra:
- `http://127.0.0.1:9090/targets` — `zelabairro` deve estar **UP**.
- `http://127.0.0.1:3000` — Grafana, com senha do `.env`; dashboard em pasta **ZelaBairro**.
- Quatro painéis: taxa de requisições, latência p95, erros 5xx e requisições em andamento. Faça um cadastro de teste e recarregue a página para gerar tráfego.

## Comprovar alerta *real* (controlado)
A regra `ZelaBairroEndpointIndisponivel` dispara quando o scrape do destino realmente falhar por pelo menos 30 segundos.
1. Tire um print `Prometheus > Status > Targets` com `zelabairro` UP.
2. Altere **temporariamente** o destino em `prometheus.yml` para `127.0.0.1:1` e execute `docker compose restart prometheus`.
3. Após 45–90 segundos, confirme `Alerts > Firing` e tire print com timestamp. Explique no PDF que foi **um teste de falha controlado**, não uma indisponibilidade real do serviço.
4. Volte o alvo original, reinicie Prometheus e mostre o retorno a UP e alerta resolvido.

## LGPD / Segurança
- Não coloque protocolos pessoais, nomes, CPF ou imagens no painel.
- O token de `/metrics` é enviado por HTTPS e fica apenas no arquivo local ignorado por Git.
- O acesso ao Grafana e Prometheus é restrito ao loopback local (127.0.0.1), não exposto na Internet.
- O dashboard local conectando à URL pública da Azure é permitido pela rubrica FIAP; não é necessário publicar Grafana na nuvem.
