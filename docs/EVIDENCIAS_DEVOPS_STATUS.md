# Quadro de conformidade — Secure DevOps (FIAP, p. 41)

As marcações indicam **arquivos preparados** vs **evidências comprovadas**. Não atribuir pontuação automaticamente.

| Critério do PDF | Pontuação | Situação 14/11 | Evidência que precisa existir |
| --- | ---: | --- | --- |
| Dockerfile enxuto, não root, Compose | parte dos 5,0 | Arquivos presentes | `docker build`, `docker compose up`, usuário não root |
| Terraform, state/tfvars protegidos, rede admin | parte dos 5,0 | **Pendente** | `terraform plan/apply`, infra e firewall real |
| GitHub Actions build/Gitleaks/Semgrep/Trivy a cada push | parte dos 4,0 | **Workflow escrito, ainda não executado no GitHub** | URL e prints de runs |
| Segredos via GitHub Secrets, deploy automático | parte dos 4,0 | **Pendente** | secrets sem revelar valores + deploy de commit |
| Execução bloqueada e depois corrigida | parte dos 4,0 | Roteiro preparado, **não executado** | prints vermelho/verde do Semgrep |
| 4 métricas de ouro e alerta disparado | 3,0 | `/metrics` da v1 pronto; **dashboard/alerta pendentes** | painel e alerta observável |
| Arquitetura, responsabilidade compartilhada, LGPD, custo, README | 2,0 | README e guia CI; **PDF completo pendente** | diagrama, tabela LGPD/custo e PDF final |

Não inventar URL, métricas, custos, screenshots ou deploy. Para a apresentação, diferenciar protótipo académico de serviço de prefeitura.
