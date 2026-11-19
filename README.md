# ZelaBairro — Plataforma Colaborativa de Ocorrências Urbanas

**FIAP · Engenharia de Software · 4º ano · Global Solution 2026.2**  
**Desafio:** CitizenTech  
**Disciplina:** Secure DevOps Tools & Cloud Computing — Prof. Cleórbete Santos  
**Projeto:** ZelaBairro — Deploy Blindado

## Equipe

| Integrante | RM |
| --- | --- |
| Matheus Farias de Lima | 554254 |
| Miguel Mauricio Parrado Patarroyo | 554007 |
| Vitor Pinheiro Nascimento | 553693 |
| Gabriel Leão | 552642 |
| Pedro Henrique Nardaci Chaves | 553988 |

## Acessos

| Recurso | Endereço |
| --- | --- |
| MVP publicado | https://zelabairro-gs2026-mathh.onrender.com/ |
| Código-fonte | https://github.com/mathhfarias/zelabairro-gs2026 |
| Pipeline de CI/CD | https://github.com/mathhfarias/zelabairro-gs2026/actions |
| Documentação da infraestrutura | [`infra-render/`](infra-render/) |
| Configuração de monitoramento | [`monitoring/`](monitoring/) |

## 1. Visão geral e ficha técnica do MVP

O ZelaBairro é uma aplicação web para o registro e o acompanhamento demonstrativo de ocorrências urbanas, como problemas de sinalização, calçadas e mobiliário público. O cidadão informa a categoria, o local e a descrição, recebe um protocolo e pode consultar o status do registro. A administração da plataforma possui área interna autenticada para visualização, exportação e atualização do status.

A proposta está alinhada ao desafio CitizenTech e ao ODS 11 — Cidades e Comunidades Sustentáveis. Trata-se de um **MVP acadêmico**, sem integração ou vínculo oficial com prefeitura, serviços de fiscalização ou órgãos municipais. Um status concluído na aplicação corresponde ao fluxo interno de demonstração, e não comprova reparo físico.

| Campo | Implementação |
| --- | --- |
| Linguagem e framework | Python 3.12, Flask e Gunicorn |
| Interface | Páginas HTML renderizadas com Jinja |
| Persistência | SQLite; banco em `/data/zelabairro.sqlite3` na nuvem |
| Containers | Docker, Docker Compose e execução com usuário não root |
| Nuvem | Render Web Service, plano Starter, região Ohio |
| Infraestrutura como código | Terraform, provider `render-oss/render` |
| Volume persistente | Disco de 1 GB montado em `/data` |
| Integração contínua | GitHub Actions, testes Flask, Gitleaks, Semgrep, Trivy e gate de qualidade |
| Registro de imagens | GitHub Container Registry (GHCR) |
| Entrega contínua | GitHub Actions → Render Deploy Hook, após os checks aprovados |
| Monitoramento | Prometheus e Grafana locais, consultando `/metrics` na Render |
| Alerta | `ZelaBairroEndpointIndisponivel`, com condição de indisponibilidade por 30 segundos |
| Segurança | Variáveis de ambiente, autenticação administrativa, CSRF, validação, cookies seguros e varredura de vulnerabilidades |

## 2. Funcionalidades e endpoints

| Rota | Função |
| --- | --- |
| `/` | Página inicial e apresentação da proposta |
| `/registrar` | Cadastro de ocorrência com validação e CSRF |
| `/consulta` | Consulta por protocolo |
| `/ocorrencia/<protocolo>` | Visualização da ocorrência e do status interno |
| `/api/ocorrencias/<protocolo>` | Consulta JSON pelo protocolo |
| `/admin/login` | Autenticação administrativa |
| `/admin` | Listagem e atualização de status, após autenticação |
| `/admin/export.csv` | Exportação CSV pela área administrativa |
| `/health` | Healthcheck da aplicação e do banco de dados |
| `/metrics` | Métricas Prometheus protegidas por Bearer Token na produção |

As categorias cadastráveis são `sinalizacao`, `mobiliario`, `calcada` e `outros`. Os estados internos são `pendente`, `em_analise` e `concluido`. O protocolo tem o formato `OC-XXXXXXXXXXXX`, com identificador aleatório hexadecimal.

## 3. Arquitetura

```text
[Cidadão / navegador]
         |
         | HTTPS
         v
[Render Web Service — Docker / Flask / Gunicorn]
         |                          |
         | SQLite                  | /health e /metrics (Bearer Token)
         v                          v
[Disco persistente /data]    [Prometheus local] --> [Grafana local]

[GitHub — main] --> [GitHub Actions — Testes, Gitleaks, Semgrep, Trivy]
                                        |
                                        v
                                 [Gate aprovado]
                                        |
                              +---------+---------+
                              |                   |
                              v                   v
                      [Imagem no GHCR]      [Render Deploy Hook]
                                                  |
                                                  v
                                          [Deploy do Web Service]

[Terraform / infra-render] --> [Web Service e disco de 1 GB]
```

O serviço utiliza HTTPS fornecido pela Render, expõe apenas o endpoint da aplicação e não publica uma porta administrativa de infraestrutura. O banco SQLite fica em volume persistente associado ao serviço. A configuração do disco é demonstrada no Terraform; o uso de banco relacional gerenciado e múltiplas instâncias não faz parte do escopo desta versão.

## 4. Execução local com Python

**Requisitos:** Git e Python 3.11 ou superior.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export APP_ENV=development
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export ADMIN_PASSWORD="defina-uma-senha-local-forte"
python -m flask --app wsgi run --debug
```

Abra `http://127.0.0.1:5000`. No ambiente de desenvolvimento, o SQLite é criado dentro de `instance/` quando não há outra configuração de `DATABASE_PATH`.

Para executar os testes:

```bash
python -m unittest discover -s tests -v
```

## 5. Execução com Docker Compose

**Requisitos:** Docker Desktop ou Docker Engine com Docker Compose.

```bash
cp .env.example .env
```

Configure `SECRET_KEY` e `ADMIN_PASSWORD` no `.env` local. Em seguida:

```bash
docker compose up --build -d
docker compose ps
docker compose logs --tail=80 app
```

A aplicação ficará disponível em `http://127.0.0.1:8000`. Para interromper, utilize `docker compose down`. O volume nomeado mantém os dados entre recriações comuns dos containers; `docker compose down -v` também remove os volumes.

O Dockerfile utiliza uma imagem Python slim, instala dependências sem cache, executa o processo com usuário não root e possui healthcheck. Na etapa de CI, o container é testado com sistema de arquivos somente leitura, diretório temporário específico e capacidades restritas.

## 6. Infraestrutura como código — Render

O diretório `infra-render/` define o Web Service do ZelaBairro em Docker, plano Starter, região Ohio, disco de 1 GB e variáveis de ambiente. O endpoint público é:

https://zelabairro-gs2026-mathh.onrender.com/

Com Terraform instalado e credenciais de Render disponíveis **somente no ambiente local**, os comandos de referência são:

```bash
cd infra-render
terraform init
terraform validate
terraform plan -out=render.tfplan
terraform apply render.tfplan
```

A criação inicial foi concluída por `terraform apply`, com um recurso adicionado. Os arquivos `terraform.tfstate`, `*.tfvars` e `*.tfplan` são excluídos do versionamento, pois podem conter informações sensíveis. A extensão `infra/` contém a alternativa de infraestrutura Azure; o ambiente publicado nesta entrega é a Render.

O deploy contínuo foi realizado pelo **Render Deploy Hook** após a aprovação do pipeline de segurança. Como o acionamento foi configurado adicionalmente ao Terraform, alterações futuras na infraestrutura exigem conciliar a configuração do provider Render com as opções atualizadas no serviço.

## 7. Pipeline DevSecOps

O workflow em `.github/workflows/devsecops.yml` é executado nos eventos de push, pull request e por acionamento manual. O fluxo inclui:

1. Testes automatizados Flask e validação de sintaxe Python.
2. Gitleaks para detectar credenciais expostas no repositório.
3. Semgrep para análise estática de segurança do código Python.
4. Build Docker, smoke test em container e Trivy para CVEs altas/críticas corrigíveis.
5. Gate de qualidade dependente da aprovação dos testes e scanners.
6. Publicação da imagem aprovada no GHCR, para pushes na `main`.
7. Acionamento do Deploy Hook da Render com URL armazenada no GitHub Actions Secret `RENDER_DEPLOY_HOOK_URL`.

O histórico registra execuções que foram bloqueadas durante os ajustes de Semgrep e Trivy, seguidas de execuções aprovadas. Na implantação demonstrada, a Render registrou o commit `eacf574`, acionado por **Deploy Hook**, com estado **Live** em 19/11/2026.

**Segredos e dados locais** nunca devem ser incluídos em commits: `.env`, `monitoring/.env`, `monitoring/metrics_token`, `*.tfvars`, `*.tfstate`, `*.tfplan` e tokens de provedores.

## 8. Observabilidade e teste de alerta

O endpoint `/metrics` utiliza a biblioteca `prometheus_client` e expõe as seguintes séries:

| Sinal | Métrica | Painel |
| --- | --- | --- |
| Tráfego | `zelabairro_http_requests_total` | Requisições por segundo |
| Latência | `zelabairro_http_request_duration_seconds` | Percentil p95 em segundos |
| Erros | `zelabairro_http_server_errors_total` | Erros HTTP 5xx por segundo |
| Saturação (indicador de concorrência) | `zelabairro_http_in_flight_requests` | Requisições simultâneas |

O Prometheus e o Grafana são executados localmente com Docker Compose em `monitoring/`, apontando para a URL pública HTTPS. O arquivo `metrics_token` é utilizado para autenticação na coleta e não pode ser versionado.

```bash
cd monitoring
cp prometheus.yml.example prometheus.yml
cp .env.example .env
# Configure o alvo HTTPS em prometheus.yml, a senha do Grafana em .env
# e o token de monitoramento no arquivo privado metrics_token.
docker compose up -d
docker compose ps
```

Acessos locais:

- Prometheus: http://127.0.0.1:9090/targets
- Alertas: http://127.0.0.1:9090/alerts
- Grafana: http://127.0.0.1:3000

Em 19/11/2026, o Prometheus registrou o alvo `zelabairro` em estado **UP** e o Grafana exibiu os quatro painéis, incluindo erros HTTP 5xx com valor zero. A regra `ZelaBairroEndpointIndisponivel`, definida em `monitoring/alerts.yml`, foi exercitada por uma simulação controlada de falha na coleta e atingiu o estado **FIRING** após 30 segundos. Após a restauração do endpoint monitorado, o alvo voltou ao estado **UP**. A simulação foi realizada na configuração local do Prometheus, sem indisponibilizar a aplicação pública.

## 9. Segurança e LGPD

O cadastro exige apenas local público, categoria e descrição da ocorrência, sem solicitar nome, CPF ou e-mail. Dados pessoais inseridos indevidamente nos campos livres podem, contudo, aparecer nas consultas por protocolo; o ambiente não deve receber relatos pessoais sensíveis. O banco e o volume são administrados pelo projeto e hospedados na infraestrutura da Render.

Controles implementados: validação no servidor, consultas SQLite parametrizadas, escaping de templates, CSRF, área administrativa com sessão autenticada, cookies HttpOnly/SameSite, cookie Secure em produção, cabeçalhos de proteção, exportação CSV com mitigação de fórmulas e acesso ao endpoint de métricas mediante token.

Na responsabilidade compartilhada, a Render gerencia a infraestrutura subjacente; o projeto gerencia aplicação, credenciais, lógica de acesso, dados, cópias de segurança, uso adequado e tratamento de eventuais incidentes. O MVP não implementa autenticação individual de cidadãos, auditoria administrativa avançada ou alta disponibilidade.

## 10. Estimativa de custo

| Recurso | Estimativa mensal |
| --- | ---: |
| Render Web Service — Starter | US$ 7,00 |
| Disco persistente — 1 GB | US$ 0,25 |
| **Total de referência** | **US$ 7,25** |

Valores de referência, sujeitos a regras de faturamento, impostos e eventuais alterações do provedor. Prometheus e Grafana foram executados localmente durante a demonstração.

## 11. Organização do repositório

```text
app/                       Aplicação Flask, rotas e banco
.github/workflows/         Pipeline GitHub Actions
.semgrep/                  Regras de análise estática
infra-render/              Terraform do ambiente Render implantado
infra/                     Alternativa Terraform para Azure
monitoring/                Prometheus, Grafana, dashboard e alertas
docs/                      Guias e documentação do projeto
tests/                     Testes automatizados
Dockerfile                 Imagem de produção
compose.yaml               Execução local da aplicação
render.yaml                Configuração auxiliar de publicação
requirements.txt           Dependências Python
wsgi.py                    Ponto de entrada Gunicorn
```

## 12. Entrega acadêmica

A demonstração técnica reúne o MVP público, a implementação em Docker, a infraestrutura provisionada via Terraform, o fluxo CI/CD, o dashboard das quatro métricas de ouro e a simulação de alerta. As capturas de tela, o diagrama, a análise de responsabilidades e a estimativa de custo constam no documento **ZelaBairro — Secure DevOps Tools & Cloud Computing**, entregue em PDF.

**Referências do projeto:** enunciado FIAP Global Solution 2026.2 — CitizenTech, especialmente as páginas 39–41; documento de alinhamento do grupo ZelaBairro.
