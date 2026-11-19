# ZelaBairro — MVP CitizenTech (FIAP GS 2026.2)

> **Um só produto para as sete disciplinas.** Este repositório inicia a aplicação central utilizada por **Secure DevOps Tools & Cloud Computing** (Cleórbete Santos) e **Business Intelligence & Startup Development** (Henio Scheidt). As evidências e entregáveis de cada disciplina são distintos.

**Status (v0.3 — 19/11/2026):** MVP validado localmente pelo grupo; **CI de GitHub Actions com testes, Gitleaks, Semgrep, Docker/Trivy e gate aprovados** conforme captura da execução #6 (commit `1b3cad7`). Esta extensão inclui **código preparado** de Terraform, publicação no GHCR, deploy OIDC e monitoramento, **ainda sem implantação Azure ou dashboard/alerta comprovados**. Não representa a conclusão automática das disciplinas.

**Próxima ação:** siga [docs/AZURE_TERRAFORM_DEPLOY.md](docs/AZURE_TERRAFORM_DEPLOY.md) para executar Terraform, publicar no Azure e colher evidências; o [guia do monitoramento](docs/MONITORAMENTO_GRAFANA.md) cobre o dashboard e o alerta. Lean Canvas validado, testes com cidadãos e pitch também permanecem pendentes.

## 1. Ficha Técnica Mestre (planejamento, preencher com evidências reais)

| Campo | Situação atual |
| --- | --- |
| Produto | ZelaBairro — Plataforma Colaborativa de Ocorrências Urbanas |
| Cidadão e território | Pessoas que usam praças e espaços públicos; território piloto **a definir** |
| Problema | Relatos de problemas em sinalizações e equipamentos urbanos podem ser difíceis de organizar/acompanhar; **hipótese a validar** |
| Proposta de valor | Registrar e consultar ocorrências por protocolo e status interno |
| Arquitetura | Flask (UI e API), SQLite, Docker/Compose, endpoint Prometheus; Terraform **código preparado, ainda sem provisionamento comprovado**; CI GitHub Actions **aprovada na execução #6 segundo evidência enviada pelo grupo** |
| Fonte de dados | Ocorrências submetidas à aplicação para fins de teste; **não existe base oficial municipal** |
| Modelos de IA | **Não implementados**; módulos externos ficam a cargo dos responsáveis |
| URL pública / repositório | **Repositório: https://github.com/mathhfarias/zelabairro-gs2026 ; URL pública Azure a definir após deploy** |
| Indicadores de impacto | **Não medidos**; planejar tempo de cadastro, conclusão e clareza |
| ODS | ODS 11 sugerido; contribuição precisa ser justificada no trabalho final |

## 2. O que funciona nesta versão

1. `GET /` — página inicial e explicação da proposta.
2. `GET/POST /registrar` — registro de uma ocorrência, com validação no servidor, token CSRF e protocolo único não sequencial.
3. `GET /consulta?protocolo=OC-...` — busca pelo protocolo.
4. `GET /ocorrencia/<id>` — consulta do registro e status interno, mesmo após atualizar a página.
5. `GET /api/ocorrencias/<id>` — JSON que outras disciplinas podem consumir.
6. `GET /admin/login` — área administrativa protegida com senha definida por variável de ambiente.
7. `GET /admin` — lista das últimas 200 ocorrências; atualização de status via POST (CSRF).
8. `GET /admin/export.csv` — CSV com todas as ocorrências, acessível somente após autenticação.
9. `GET /health` — saúde básica da aplicação e conexão com o banco.
10. `GET /metrics` — métricas HTTP Prometheus de tráfego, latência, erros 5xx e requisições em andamento.

O status `concluido` significa **fechado no fluxo de demonstração**, não reparo físico ou atendimento público.

## 3. Como rodar no Mac (VS Code)

Requisitos: Python 3.11+ e Git. No terminal, dentro desta pasta:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Crie variáveis para a execução local, em **sua sessão do terminal** (não são senhas reais):

```bash
export APP_ENV=development
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export ADMIN_PASSWORD="escolha-uma-senha-forte-para-os-testes"
python -m flask --app wsgi run --debug
```

Abra **http://127.0.0.1:5000** e teste Registrar → Consultar. A área administrativa fica em `/admin`. O arquivo de banco é criado automaticamente em `instance/zelabairro.sqlite3` e **não deve ser enviado ao GitHub**.

Para testes automatizados:

```bash
python -m unittest discover -s tests -v
```

## 4. Como rodar com Docker Compose (desenvolvimento/validação)

Requisitos: Docker Engine ou Docker Desktop e Docker Compose v2.

```bash
cp .env.example .env
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

Coloque a chave gerada no campo `SECRET_KEY` dentro do `.env` e defina uma senha forte e exclusiva em `ADMIN_PASSWORD`. **Nunca comite `.env`**. Em seguida:

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f app
```

Acesse **http://localhost:8000**. Este Compose usa `APP_ENV=development` apenas para testes locais HTTP. Antes de disponibilizar na Internet, use `APP_ENV=production`, HTTPS, secrets fortes e políticas de firewall.

Para verificar volume persistente:

```bash
docker compose down
docker compose up -d
```

O volume nomeado `zelabairro_data` permanece. **Não use `down -v`** se quiser preservar os dados.

Para encerrar: `docker compose down`.

> **Atenção:** O Compose limita a publicação a `127.0.0.1:8000` e não é um deploy público. Para publicação, adotar proxy HTTPS, `APP_ENV=production`, firewall e controle de acesso. Em produção o cookie de sessão tem a marca `Secure`.

## 5. Contrato de dados (versão inicial)

Uma ocorrência segue o dicionário do planejamento do grupo, com o campo `id` como protocolo público:

```json
{
  "id": "OC-A1B2C3D4E5F6",
  "categoria": "sinalizacao",
  "local": "Praça Exemplo",
  "descricao": "Placa com suporte danificado",
  "status": "pendente",
  "data": "2026-11-13T14:00:00+00:00",
  "data_atualizacao": "2026-11-13T14:00:00+00:00"
}
```

**Este JSON é ilustrativo, não dado real.** Campos podem ser adicionados pelos módulos, desde que o grupo aprove o contrato e preserve compatibilidade. Nesta versão, não há foto, OCR, IA generativa ou RPA integrados.

Categorias permitidas: `sinalizacao`, `mobiliario`, `calcada`, `outros`.
Status permitidos: `pendente`, `em_analise`, `concluido`.

### Integrações futuras

- **Big Data:** extrair ocorrências via CSV administrativo (sem credenciais no código) e gerar indicadores reais.
- **Computer Vision:** acrescentar imagem autorizada e um campo de texto extraído após implementação do módulo.
- **Generative AI:** sugerir descrição e categoria, sempre com confirmação humana.
- **RPA:** consumir fila de triagem e devolver retorno interno; sem dizer que se trata de protocolo oficial.
- **Maker Lab:** relacionar o objeto redesenhado a uma ocorrência.
- **Startup:** demonstrar registro e consulta no pitch; medir valor com usuários reais e consentimento.

## 6. Segurança já considerada

- SQL parametrizado e escaping HTML automático (Jinja).
- Proteção CSRF nos formulários POST.
- Autenticação da área administrativa por senha de ambiente; sem senha hardcoded para produção.
- Cookies de sessão HttpOnly, SameSite Lax e Secure no perfil `production`.
- Cabeçalhos `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`.
- Limite total de corpo de requisição de 64 KB; sem upload de imagens na versão 1.
- Sem coleta de nome, CPF, e-mail ou geolocalização pessoal.
- Banco persistente, Dockerfile com usuário não root, sistema de arquivos do container como somente leitura e volume dedicado.
- Sanitização de valores potencialmente interpretáveis como fórmulas na exportação CSV.

**Limites desta versão:** não há rate limiting distribuído, MFA, auditoria de admin ou política formal de retenção. A consulta por protocolo expõe local e descrição; não incluir dados pessoais ou relatos sensíveis. Não publicar dados de testes identificáveis sem autorização. O endpoint `/metrics` está público; restringir sua exposição ao publicar em ambiente real, se necessário. Esta versão não foi auditada para uso em produção.

## 7. Métricas já instrumentadas

| Categoria das 4 métricas de ouro | Métrica instrumentada | Observação |
| --- | --- | --- |
| Tráfego | `zelabairro_http_requests_total` | Contador por rota/método/status |
| Latência | `zelabairro_http_request_duration_seconds` | Histograma por rota/método |
| Erros | `zelabairro_http_server_errors_total` | Contador de respostas HTTP 5xx |
| Saturação (indicador inicial) | `zelabairro_http_in_flight_requests` | Requisições em andamento; complementar com recursos de infraestrutura |

`GET /metrics` disponibiliza os dados em formato Prometheus. **Dashboard e alerta têm arquivos preparados em `monitoring/`, mas ainda exigem execução e prints reais.** A rubrica de DevOps exige evidência de ambos.

## 8. Próximas etapas para cumprir a rubrica oficial (p. 39–41)

- [x] Código-base da aplicação central com testes automatizados escritos (**executar testes antes de demonstrar funcionamento**).
- [x] Dockerfile enxuto, usuário não root, Compose e volume persistente (arquivos criados; validar execução Docker).
- [x] Instrumentação inicial das quatro métricas de ouro (código incluído; **executar e validar** no dashboard).
- [ ] Provisionamento cloud real por Terraform; state e tfvars fora do repositório; rede administrativa restrita.
- [x] Arquivo GitHub Actions preparado para executar a cada push: testes, build, Gitleaks, Semgrep e Trivy (**execução #6 aprovada segundo evidência do grupo**).
- [x] Execuções bloqueadas por Semgrep/Trivy e posterior CI aprovada (#6): **guardar prints dos runs e diffs dos commits para o PDF**.
- [ ] Deploy automático em infraestrutura Terraform com URL HTTPS pública.
- [ ] Dashboard com quatro métricas e alerta demonstravelmente disparado.
- [ ] Diagrama de arquitetura, responsabilidade compartilhada, LGPD, estimativa de custo.
- [ ] PDF único com links clicáveis e prints reais de todas as evidências.

### Startup (Henio, p. 31–34)

- [ ] Validar problema, público e território piloto.
- [ ] Consolidar **9 blocos do Lean Canvas** e distinguir validação real vs. hipótese.
- [ ] Documentar transição desde CP1 se a ideia anterior era diferente.
- [ ] Modelo de negócio com proposta de valor, fontes de receita, preço, canais e métricas.
- [ ] Testar a jornada do MVP com usuários reais e registrar resultados.
- [ ] Vídeo-pitch **até 5 minutos**, todos participam, com demonstração do mesmo MVP.
- [ ] PDF único com Canvas, negócio e links clicáveis de vídeo, MVP e GitHub.

## 9. Entrega e prazo

**Data no enunciado oficial:** 19/11/2026, às 23h55. Links públicos acessíveis durante a correção; um único envio por disciplina. Cada disciplina exige seus próprios entregáveis. Não considerar a criação deste repositório como a conclusão de qualquer disciplina.

## 10. Referências

- FIAP. **Desafio FIAP: CitizenTech — Engenharia de Software, 4º ano, Global Solution 2026.2**: páginas 18–24, 31–34 e 39–41.
- Grupo. **ZelaBairro — Documento de Alinhamento v0.3 (09/11/2026)**: definição do produto, jornada, contrato inicial e responsáveis.

> Em caso de divergência, prevalecem o enunciado e as orientações do professor responsável.


---

## Extensão de cloud e observabilidade — Global Solution (19/11/2026)

**Este pacote mantém o ZelaBairro como produto único para Secure DevOps e Startup.**

- **GitHub Actions:** os jobs existentes de testes/Gitleaks/Semgrep/Trivy continuam; após aprovação na `main`, uma imagem Docker é publicada em GHCR. Com a variável `AZURE_WEBAPP_NAME`, o deploy via Azure OIDC é acionado automaticamente.
- **Terraform:** pasta [`infra/`](infra/) provisiona RG, App Service Plan Linux B1 e Web App HTTPS com imagem GHCR, sem abrir portas administrativas.
- **Banco SQLite:** no Azure, usar `/home/zelabairro.sqlite3` com storage persistente habilitado, validando permissões de escrita e retenção do protocolo após restart. Solução acadêmica de instância única, não banco de produção escalável.
- **Métricas:** `/metrics` usa bearer token em produção; Grafana e Prometheus locais monitoram os dados pela URL pública e possuem regra de alerta controlado.
- **Guia de infraestrutura:** [`docs/AZURE_TERRAFORM_DEPLOY.md`](docs/AZURE_TERRAFORM_DEPLOY.md).
- **Guia de monitoramento:** [`docs/MONITORAMENTO_GRAFANA.md`](docs/MONITORAMENTO_GRAFANA.md).
- **Checklist de evidências:** [`docs/CONFERENCIA_ENTREGA.md`](docs/CONFERENCIA_ENTREGA.md).

**Não implementado automaticamente:** criação de recursos Azure, vínculo de identidade OIDC no Entra, registro público do GHCR, inserção de secrets e execução real do monitoramento. Exigem conta, permissões e provas de execução do grupo.
