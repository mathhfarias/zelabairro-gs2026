# Plano integrado — Secure DevOps + Startup

## Regra: mesmo produto, entregas diferentes

**Produto único:** ZelaBairro (registro e consulta de ocorrências urbanas). Não desenvolver um aplicativo separado para Startup e outro para Secure DevOps.

### Caminho demonstrável

1. Cidadão abre a URL pública.
2. Informa local, categoria e descrição; envia ocorrência.
3. Backend grava um registro em SQLite; apresenta protocolo `OC-...`.
4. Cidadão consulta o mesmo protocolo e vê o status interno.
5. Equipe de testes acessa o painel administrativo, muda o status e o cidadão vê a atualização.

A mesma jornada sustenta o deploy e monitoramento de **Secure DevOps** e o vídeo-pitch do **Startup**.

### Secure DevOps (Cleórbete) — p. 39–41

| Nota | Exigência | Evidência que será necessária |
| --- | --- | --- |
| 2/5 | Dockerfile enxuto, não root, Compose, sem segredos na imagem | Docker build/ps, compose up, inspecionar usuário |
| 3/5 | Infra criada por Terraform, tfstate/tfvars fora do repo, sem admin aberta ao mundo | `terraform plan/apply`, recursos cloud, regras de rede |
| 4 | GitHub Actions build + Gitleaks + Semgrep + Trivy a cada push, Secrets, deploy automático, falha e correção | histórico de workflow, logs de bloqueio/correção, URL |
| 3 | Dashboard das quatro métricas de ouro + alerta disparado | painel com tráfego/latência/erros/saturação e prova do alerta |
| 2 | Arquitetura, responsabilidade compartilhada, LGPD, custos e README | PDF, diagrama, planilha/resumo de custos, README |

**Atenção:** os itens acima descrevem o que precisa ser demonstrado. Apenas o que está implementado deve ser marcado como concluído.

### Startup (Henio) — p. 31–34

| Nota | Exigência | Evidência necessária |
| --- | --- | --- |
| 2 | Lean Canvas, nove blocos e aprendizado desde CP1 | Quadro consolidado, hipóteses e mudanças documentadas |
| 2,5 | Modelo de negócio: proposta, receita, preço, canais e métricas | Coerência e premissas justificadas |
| 2,5 | História problema → cidadão → solução → impacto em até 5 min, todos participam | Link público do vídeo |
| 3,5 | Fluxo real em URL pública, do clique inicial à consulta | Gravação contínua sem telas falsas |
| 3,5 | Valor entregue com evidência | Teste documentado com usuários, observação ou métricas reais |

## Três pendências imediatas da equipe

1. Confirmar quem manterá o núcleo Flask e o repositório oficial.
2. Definir território piloto e uma categoria principal para a narrativa do produto.
3. Consultar Henio sobre como justificar a troca de ideia em relação à CP1, se aplicável.

Não incluir dados sintéticos como dados reais e não alegar parceria com prefeitura.
